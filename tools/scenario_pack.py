#!/usr/bin/env python3
"""Turn a short business brief into a complete scroll-motion production pack.

Usage:
  python tools/scenario_pack.py brief.json --out pack
  python tools/scenario_pack.py --list                  # industries in references/playbooks.json

brief.json (all optional except business):
  {
    "business": "Acme Chairs", "product": "Oak lounge chair", "industry": "furniture-interior",   # or "auto"
    "object": "the chair", "setting": "a calm modern home at dusk",
    "tone": "calm, assured", "tool": "veo-flow",          # veo-flow | kling | runway | sora | higgsfield | generic
    "legs": 5, "seconds_per_leg": 4, "goal": "portfolio", "audience": "design-minded homeowners",
    "continuity_token": "Acme oak lounge chair", "style": "photoreal architectural photography"
  }

Writes: SCENARIO.md (storyboard, page copy, plan), PROMPTS.md (stills + chained video prompts),
content.json (layered hero draft), recipe.json (assemble.py skeleton).
Everything is a DRAFT for you and the user to refine; the playbook gives structure, you add the specifics.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLAYBOOKS = os.path.join(HERE, "..", "references", "playbooks.json")

KEYWORDS = {
    "furniture-interior": ["furniture", "sofa", "couch", "interior", "decor", "curtain", "chair", "lighting", "مبل", "مبلمان", "دکور", "پرده", "صندلی"],
    "real-estate-architecture": ["real estate", "villa", "architect", "construction", "developer", "property", "املاک", "ساختمان", "معماری", "ویلا", "سازنده"],
    "restaurant-cafe": ["restaurant", "cafe", "coffee", "bakery", "pizza", "bar", "رستوران", "کافه", "قنادی", "نانوایی"],
    "hotel-travel": ["hotel", "resort", "travel", "tour", "villa stay", "هتل", "اقامتگاه", "گردشگری", "سفر"],
    "jewelry-watch": ["jewelry", "jewellery", "gold", "watch", "ring", "necklace", "طلا", "جواهر", "ساعت", "گردنبند"],
    "beauty-perfume-skincare": ["perfume", "skincare", "cosmetic", "beauty", "fragrance", "عطر", "آرایشی", "پوست", "زیبایی"],
    "fashion": ["fashion", "clothing", "apparel", "garment", "textile", "dress", "لباس", "مد", "پارچه", "پوشاک"],
    "automotive": ["car", "auto", "motorcycle", "vehicle", "ev", "خودرو", "ماشین", "موتور"],
    "tech-saas-app": ["software", "saas", "app", "ai", "platform", "startup", "نرم‌افزار", "اپلیکیشن", "هوش مصنوعی"],
    "clinic-dental-wellness": ["clinic", "dental", "dentist", "spa", "wellness", "therapy", "کلینیک", "دندان", "پزشک", "اسپا", "درمان"],
    "food-beverage-packaging": ["food", "beverage", "snack", "tea", "saffron", "juice", "packaged", "غذا", "نوشیدنی", "چای", "زعفران", "فرآورده"],
    "fitness-sport": ["gym", "fitness", "sport", "training", "crossfit", "باشگاه", "ورزش", "تناسب"],
    "education-course": ["course", "academy", "school", "education", "bootcamp", "training course", "آموزش", "دوره", "آکادمی", "مدرسه"],
    "legal-finance-consulting": ["law", "legal", "finance", "consulting", "accounting", "advisory", "حقوقی", "وکیل", "مشاوره", "حسابداری", "مالی"],
    "craft-workshop-manufacturing": ["workshop", "craft", "maker", "manufactur", "leather", "woodwork", "ceramic", "کارگاه", "صنایع دستی", "چرم", "سفال", "تولیدی"],
}

TOOLS = {
    "veo-flow": "Google Flow (Veo 3.1): use Frames to Video with the START frame only (end frames are only hints); 1080p; 4-8 s per clip; no audio needed.",
    "kling": "Kling: image-to-video with a start frame; use the highest quality mode; 5 s clips; avoid the end-frame option for chains.",
    "runway": "Runway: image-to-video from the start frame; keep one camera move per clip; 5-10 s.",
    "sora": "Sora: image-to-video from the start frame; ask for a single locked-direction camera move.",
    "higgsfield": "Higgsfield: generate_image for stills, generate_video from a start image; check balance and cost before generating.",
    "generic": "Any image-to-video model: start frame = last frame of the previous clip, no end frame, constant speed.",
}


def pick_industry(brief, data):
    ind = (brief.get("industry") or "auto").lower()
    if ind in data["industries"]:
        return ind
    text = " ".join(str(brief.get(k, "")) for k in ("business", "product", "object", "setting", "audience")).lower()
    best, score = "generic", 0
    for k, words in KEYWORDS.items():
        s = sum(1 for w in words if w in text)
        if s > score:
            best, score = k, s
    return best


def fill(s, ctx):
    for k, v in ctx.items():
        s = s.replace("{" + k + "}", v)
    return s


def cap(s):
    return s[:1].upper() + s[1:] if s else s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("brief", nargs="?")
    ap.add_argument("--out", default="pack")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    data = json.load(open(PLAYBOOKS, encoding="utf-8"))
    if a.list or not a.brief:
        for k, v in data["industries"].items():
            print(f"{k:32s} {v['title']}  ->  {v['journey']}")
        return
    brief = json.load(open(a.brief, encoding="utf-8"))
    if not brief.get("business"):
        sys.exit("brief.json needs at least a 'business' name")
    ind = pick_industry(brief, data)
    pb = data["industries"][ind]
    biz = brief["business"]
    product = brief.get("product") or biz
    obj = brief.get("object") or pb["object"]
    setting = brief.get("setting") or pb["setting"]
    ctx = {"business": biz, "product": product, "object": obj, "setting": setting}
    legs = pb["legs"][: int(brief.get("legs", len(pb["legs"])))]
    sec = int(brief.get("seconds_per_leg", 4))
    tool = brief.get("tool", "generic")
    token = brief.get("continuity_token") or product
    style = brief.get("style") or "photoreal cinematic photography, soft film grain"
    tone = brief.get("tone") or pb["tone"]
    n = len(legs)
    os.makedirs(a.out, exist_ok=True)

    global_style = f"{style}, {setting}, 16:9, subject centered in the middle 60% of the frame, no text, no letters, no logos, no watermark"

    # ---------- SCENARIO.md ----------
    L = [f"# {biz}: scroll-motion scenario", "",
         f"**Industry playbook:** {pb['title']} (`{ind}`)  \n**Goal:** {brief.get('goal', 'portfolio')}  \n**Audience:** {brief.get('audience', 'to be confirmed')}  \n**Tone:** {tone}",
         "", f"## Concept", f"One continuous camera move: **{pb['journey']}**. The visitor scrolls, the camera moves; nothing cuts.", "",
         f"## Storyboard ({n} legs x {sec} s = {n * sec} s of footage)", "",
         "| Leg | Beat | Camera move | The visitor sees | Copy beat |", "|---|---|---|---|---|"]
    for i, g in enumerate(legs, 1):
        L.append(f"| {i} | {g['beat']} | {fill(g['camera'], ctx)} | {fill(g['sees'], ctx)} | {fill(g['overlay'], ctx)} |")
    pl = pb["layers"]
    L += ["", "## Page layers (draft copy for `hero.layers`)", "",
          f"* **Headline (2 lines):** {' / '.join(pl['headline'])}",
          f"* **Paragraph:** {fill(pl['paragraph'], ctx)} **{fill(pl['bold'], ctx)}**",
          f"* **Big statement:** {fill(pl['big'], ctx)}",
          "", "## Look", f"* **Palette:** {brief.get('palette') or pb['palette']}", f"* **Type:** {pb['type']}", "",
          "## Risks for this industry"] + [f"* {r}" for r in pb["risks"]] + [
          "", "## Production plan",
          f"1. Make **stills** S1..S{n + 1} (see PROMPTS.md). Check they look like one world; S1 is the first frame of the whole scroll.",
          f"2. Generate **leg 1** from S1. Test one leg before the rest.",
          f"3. For every next leg run `python tools/last_frame.py clip_k.mp4 start_k+1.png` and use that PNG as the start frame (no end frame).",
          f"4. Put the clips in `clips/01.mp4 ... {n:02d}.mp4`, then run `python tools/analyze_clips.py clips/*.mp4` and follow the verdicts.",
          "5. Assemble, review frames, encode, build the page.", "",
          f"**Tool notes ({tool}):** {TOOLS.get(tool, TOOLS['generic'])}", "",
          f"**Estimated generations:** {n + 1} stills + {n} clips (+ re-takes; plan for ~1.5x)."]
    open(os.path.join(a.out, "SCENARIO.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")

    # ---------- PROMPTS.md ----------
    P = [f"# {biz}: prompts", "",
         "## 0. Shared style (repeat verbatim in every still prompt)", "```", global_style, "```",
         f"**Continuity token (keep identical everywhere):** `{token}`", "",
         "## 1. Stills (image model: Nano Banana / Gemini, GPT-image, Midjourney, Higgsfield)",
         "Attach the previous still as a reference so the world stays identical.", ""]
    P += [f"### S1: first frame of the scroll", "```",
          f"{global_style}. Wide establishing view at the very start of the move: {setting}; {token} small in the distance, lit and readable.", "```", ""]
    for i, g in enumerate(legs, 1):
        P += [f"### S{i + 1}: end of leg {i} ({g['beat']})", "```",
              f"{global_style}. Same world as the previous still, after this camera move: {fill(g['camera'], ctx)}. What the viewer sees now: {fill(g['sees'], ctx)}. Only the camera position changed; {token} identical.", "```", ""]
    P += ["## 2. Video prompts (chain: one continuous move)",
          "Settings: 1080p, 24 fps, no audio, " + f"{sec} s per clip, **no end frame**.", ""]
    guard = f"Do NOT rotate {obj}; it is a fixed object. Move the virtual camera only." if ind not in ("tech-saas-app", "education-course") else ""
    for i, g in enumerate(legs, 1):
        start = "S1 (still)" if i == 1 else f"last frame of clip {i - 1}  (`python tools/last_frame.py clip{i - 1}.mp4 start{i}.png`)"
        if i == 1:
            txt = f"Slow steady {fill(g['camera'], ctx)} at constant speed, eye-level camera, {fill(g['sees'], ctx)}, nothing else changes, no ease-in, no ease-out."
        else:
            txt = (f"Continue the same forward movement at the same constant speed: {fill(g['camera'], ctx)}, no turning, the {setting} and {token} stay exactly the same, no ease-in, no ease-out.")
        P += [f"### Clip {i}: {g['beat']}", f"Start frame: {start}", "```", (txt + (" " + guard if guard else "")).strip(), "```", ""]
    P += ["If the camera orbits or shows another part of the space, append:", "```",
          "The camera keeps looking in the same direction. Do not turn, orbit or show a different part of the space.", "```", "",
          "## 3. Gap clip (only if `analyze_clips.py` reports a seam of 8-14 eq-frames)",
          "Start = last good frame of clip k, end = first frame of clip k+1. Describe the visible move in one sentence:", "```",
          "A very slow, steady camera move inside the same space: the camera glides slightly forward and a little to the <side> while lowering a few centimeters. The camera keeps looking in the same direction, no turning, no tilting up. Constant speed, no ease-in, no ease-out. Everything else stays exactly the same.",
          "```", "",
          "## 4. Never generate", "* Text, logos, labels, UI screens: add them in HTML.", "* Faces and hands in close-up.", "* A different lens, time of day or colour grade between clips."]
    open(os.path.join(a.out, "PROMPTS.md"), "w", encoding="utf-8").write("\n".join(P) + "\n")

    # ---------- content.json ----------
    caps = [{"from": round(i / n, 3), "to": round((i + 1) / n, 3), "text": fill(g["overlay"], ctx)} for i, g in enumerate(legs)]
    content = {
        "languages": ["en"], "default_lang": "en", "sections": ["offerings", "about", "cta"],
        "brand": {"name": biz.upper(), "descriptor": {"en": pb["title"]}, "tagline": {"en": fill(pl["bold"], ctx)}},
        "hero": {"mode": "video", "preset": "layers", "captions": caps, "layers": {
            "nav": ["Collection", "Craft", "Materials", "Contact"], "navButton": "Request a Quote",
            "paragraph": {"pre": fill(pl["paragraph"], ctx), "bold": fill(pl["bold"], ctx)},
            "headline": [fill(x, ctx) for x in pl["headline"]], "cta": "Explore " + product,
            "big": fill(pl["big"], ctx), "footerTag": "Made to order",
            "columns": [{"title": product, "text": "One short sentence about it."}, {"title": "How we work", "text": "One short sentence about the process."}],
            "card": {"title": "Ready To Begin?", "button": "Get In Touch", "href": "mailto:hello@example.com"}}},
        "offerings": {"eyebrow": {"en": "THE COLLECTION"}, "title": {"en": "Three things we do well."}, "items": [
            {"name": {"en": product}, "blurb": {"en": "One sentence."}, "tag": {"en": "Featured"}},
            {"name": {"en": "Second"}, "blurb": {"en": "One sentence."}}, {"name": {"en": "Third"}, "blurb": {"en": "One sentence."}}]},
        "about": {"title": {"en": fill(pl["bold"], ctx)}, "body": {"en": "Two or three calm, specific sentences."}},
        "cta": {"title": {"en": "Make it yours."}, "body": {"en": "Tell us what you have in mind."}, "button": {"en": "Get in touch"}, "href": "mailto:hello@example.com"},
    }
    json.dump(content, open(os.path.join(a.out, "content.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)

    # ---------- recipe.json ----------
    segs = [{"type": "clip", "src": f"clips/{i:02d}.mp4", "start": 0, "label": f"clip {i} ({legs[i - 1]['beat']})"} for i in range(1, n + 1)]
    recipe = {"out_dir": "work", "size": [1920, 1080], "fps": 24, "crf": 10, "segments": segs, "equalize": {"target": 1.5, "maxskip": 4}}
    json.dump(recipe, open(os.path.join(a.out, "recipe.json"), "w", encoding="utf-8"), indent=2)
    print(f"Pack written to {a.out}/  (industry: {ind}, {n} legs x {sec}s)\n  SCENARIO.md  PROMPTS.md  content.json  recipe.json")


if __name__ == "__main__":
    main()
