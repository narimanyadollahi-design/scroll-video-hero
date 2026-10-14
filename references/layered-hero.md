# Layered hero (the reference-style text system)

`templates/site/components/HeroScroll.tsx` renders a pinned video and these layers. All timings are fractions `p` (0..1)
of the hero scroll distance; the video time is `p * duration`. Edit the numbers in `paint(p)`.

| Layer | Position / size | Behaviour |
|---|---|---|
| Nav | fixed top: logo (or brand text) left, dark pill menu (uppercase, tracked), white button right | stays; gets a blur bar after 40 px |
| Paragraph | top-right, ~1% of viewport width font, right-aligned, last sentence bold | scrolls up at 0.52x, fades 0.10-0.26 |
| Headline | bottom-left, `clamp(2.1rem, 4.7vw, 5.4rem)`, 2 lines, Title Case, tight leading | scrolls up at 0.78x, fades 0.26-0.38 |
| CTA | bottom-right dark box + arrow box | fades 0.12-0.24 |
| Big statement | bottom-left, `clamp(1.3rem, 3.7vw, 4.3rem)` | rises 0.34-0.50; words light 0.44-0.64 (opacity .16 -> 1); leaves 0.78-0.92 |
| Columns | 2 small columns (+ logo on desktop) | in 0.56-0.68, out with the statement |
| Closing card | full-width dark card at the bottom | rises 0.84-0.97 while the video ends on the close-up |

Design rules taken from the reference recording:
* One continuous camera move; the text moves over a pinned video (parallax), never over a cut.
* Bright frames need soft scrims (top 38vh, bottom 55vh), not a visible vignette.
* Type: one serif for everything (nav labels in small uppercase with tracking). Sizes are relative to viewport width.
* Mobile: columns become 2 columns at 4vh, the statement sits at 26vh with a slightly smaller minimum size.
  Verify with `getBoundingClientRect()` at 375x812 that the statement bottom is above the columns top at p = 0.55-0.76.

Content lives in `content.json` -> `hero.layers` (`nav`, `navButton`, `paragraph{pre,bold}`, `headline[]`, `cta`, `big`,
`footerTag`, `columns[]`, `card{title,button,href}`). Optional `brand.logo` (e.g. `/logo.png`, transparent PNG).

Fonts: default is Google Fonts Lora via `theme.json -> fonts_url`. To self-host, drop the `.woff2` files in `public/fonts/`,
add `@font-face` rules to `app/globals.css`, set `fonts_url` to `""`.
