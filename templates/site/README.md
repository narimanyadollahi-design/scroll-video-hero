# Site template

Next.js + GSAP + Tailwind with the layered scroll hero. Content in `content.json` (`hero.layers`), colours/fonts in `theme.json`.

```bash
npm install
python ../../tools/make_placeholder.py public    # placeholder hero until you have footage
npm run dev
# real footage:
python ../../tools/encode_hero.py master.mp4 --out public --content content.json
```

Put `hero.mp4`, `hero-mobile.mp4`, `hero-poster.jpg` (and an optional `logo.png`, then set `brand.logo`) in `public/`.
