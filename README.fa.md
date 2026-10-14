# scroll-video-hero

[English](README.md) · **فارسی**

**اسکرول موشن برای هر کسب‌وکار.** با اسکرول کاربر، دوربین حرکت می‌کند: یک حرکت پیوسته، بدون برش، داخل یک صفحه‌ی لندینگ
(نوار بالا، تیتر، بلوک متنی که کلمه‌به‌کلمه روشن می‌شود، و کارت پایانی).

این یک اسکیل Claude Code است، همراه با ابزارهایی که آن را اجرا می‌کنند:

1. **می‌فهمد چه چیزی دارید:** مرجعی که دوست دارید («مثل این ویدیو»)، فقط یک ایده، هیچ‌چیز، یا کلیپ‌های آماده.
2. **سناریو و پرامپت می‌نویسد** (تصویرهای کلیدی + پرامپت کلیپ‌های زنجیره‌ای) برای Veo/Flow، Kling، Runway، Sora، Higgsfield و غیره.
3. **کلیپ‌هایتان را تعمیر و یکی می‌کند** و یک مستر بی‌درز می‌سازد: هر درز را اندازه می‌گیرد، می‌گوید کدام راه‌حل لازم است،
   پرش، توقف و فریم خراب را رفع می‌کند و بازنگری با شماره‌ی فریم می‌دهد.
4. **صفحه را می‌سازد** (قالب Next.js + GSAP + Tailwind) و **بسته‌ی آفلاین برای فلش** درست می‌کند.

> مدل‌های ویدیو فریم پایان را رعایت نمی‌کنند؛ پس کلیپ‌هایی که جدا ساخته شوند تقریباً هیچ‌وقت به هم نمی‌رسند. این ابزارها هر درز را
> اندازه می‌گیرند و می‌گویند باید برید، پل زد، کلیپ gap ساخت یا کلیپ را از آخرین فریم دوباره گرفت، به‌جای حدس‌زدن.

## نصب به‌عنوان اسکیل Claude Code

```bash
git clone https://github.com/narimanyadollahi-design/scroll-video-hero ~/.claude/skills/scroll-video-hero
pip install -r ~/.claude/skills/scroll-video-hero/requirements.txt      # opencv-python, numpy, Pillow
```
همچنین لازم است: FFmpeg و FFprobe در PATH، و Node.js ‏18 به بالا (برای صفحه).

بعد فقط با Claude حرف بزنید:
* «برای نانوایی‌ام اسکرول موشن می‌خواهم، از کجا شروع کنم؟» ← چند سؤال می‌پرسد و یک مفهوم پیشنهاد می‌دهد.
* «افکت اسکرول این ویدیو را می‌خواهم» + یک ضبط صفحه ← زبان حرکتش را می‌خواند و برای کسب‌وکار شما تطبیق می‌دهد.
* «اینها کلیپ‌های من است، بین برش‌ها می‌پرد» ← اندازه می‌گیرد، تعمیر و یکی می‌کند.

## داخل پروژه چیست

```
SKILL.md                 گردش کاری که Claude دنبال می‌کند (ورودی ← سناریو ← کلیپ‌ها ← صفحه ← بسته)
tools/
  scenario_pack.py       بریف کسب‌وکار ← SCENARIO.md، PROMPTS.md، content.json، recipe.json   (۱۵ پلی‌بوک صنعت)
  analyze_reference.py   ویدیو یا ضبط مرجع ← اعداد + شیت شماره‌دار
  analyze_clips.py       کلیپ‌های شما ← سرعت، ease، پرش پایانی، فاصله‌ی درزها + توصیه + جفت‌تصویر هر درز
  assemble.py            recipe ← یک مستر (کلیپ، پل جریان نوری، کلیپ gap با تغییر سرعت، یکنواخت‌سازی)
  review_frames.py       فریم‌های شماره‌دار + شیت + نقشه‌ی بخش‌ها، برای «فریم‌های ۲۷۷ تا ۲۸۱ خراب است»
  encode_hero.py         دسکتاپ ۱۰۸۰p + موبایل ۷۲۰×۱۲۸۰ + پوستر (گروه کوتاه)
  check_site.py          بررسی پیش از انتشار: GOP، حجم، پرش، توقف، متن‌های جایگزین
  package_static.py      خروجی استاتیک + سرور کوچک با پشتیبانی Range + اجراکننده‌ها (فلش)
  last_frame.py  bridge.py  equalize_speed.py  make_placeholder.py
templates/site/          صفحه‌ی Next.js با هیروی لایه‌ای (حالت‌ها: layers | captions؛ زمان‌بندی در content.json)
templates/usb/           اجراکننده‌ی آفلاین
references/              intake.md، playbooks.json، reference-analysis.md، models.md،
                         prompts-video-models.md، layered-hero.md، lessons.md
examples/recipe.example.json
```

## شروع سریع بدون Claude

```bash
python tools/scenario_pack.py --list
echo '{"business":"Atelier Noor","product":"Leather bag","industry":"auto","tool":"veo-flow"}' > brief.json
python tools/scenario_pack.py brief.json --out pack            # pack/SCENARIO.md را بخوانید و با pack/PROMPTS.md بسازید

python tools/analyze_clips.py clips/01.mp4 clips/02.mp4 ...    # توصیه‌ی هر درز را دنبال کنید
python tools/assemble.py pack/recipe.json                      # بعد از ویرایش recipe
python tools/review_frames.py work/master_eq.mp4 --map work/master.map.json --out frames_review
python tools/encode_hero.py work/master_eq.mp4 --out templates/site/public --content templates/site/content.json
python tools/check_site.py templates/site
python tools/package_static.py templates/site --out dist-usb --name "My Brand" --bundle-node
```

## درزها چطور دسته‌بندی می‌شوند
فاصله‌ی دوربین با **eq-frame** سنجیده می‌شود (چند فریم حرکت عادی دوربین بین دو فریم است):

| فاصله | راه‌حل |
|---|---|
| کمتر از ۲٫۵ | برش ساده |
| ۲٫۵ تا ۸ | پل کوتاه با جریان نرم یا کلیپ gap تولیدشده |
| ۸ تا ۱۴ | کلیپ gap از مدل ویدیو (شروع = A، پایان = B) |
| بیشتر از ۱۴ | کلیپ بعدی را از آخرین فریم کلیپ قبلی دوباره بگیرید |

نتایج اندازه‌گیری‌شده و استدلال: `references/lessons.md`.

## محدودیت‌ها (صادقانه)
* جریان نوری هندسه نمی‌سازد: بالای حدود ۱۵ eq-frame تصویر را خراب می‌کند؛ ابزارها این را می‌گویند و پنهانش نمی‌کنند.
* اسکیل پرامپت می‌نویسد و فیلم را تعمیر می‌کند؛ خودِ تولید در مدل ویدیوی شما (یا یک MCP/API که دارید) انجام می‌شود.
* هیرو یک ویدیو است که با `currentTime` اسکرول می‌شود. روی iPhone (Safari) و Android واقعی تست کنید.
* متن برند، لوگو و UI در HTML اضافه می‌شود، هرگز داخل فیلم تولیدی.

## مجوز
MIT. فایل `LICENSE` را ببینید.
