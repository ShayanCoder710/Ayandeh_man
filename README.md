# Ayandeh-man (آینده من)

A static site (HTML + CSS + vanilla JS) that helps Iranian students finishing 9th grade pick
their 10th-grade high-school track (ریاضی, تجربی, انسانی, or فنی‌وحرفه‌ای). It runs a short
personality-and-interest test, scores the answers against the four tracks plus a set of
work-style traits, and recommends the track that fits the person.

There is no backend and no database: all content ships as JSON in `data/`, all scoring runs in
the browser, ratings are stored in the visitor's own `localStorage`, and test results are
shareable as a single URL with the answers encoded in the query string.

## What it does

- Personality and interest test: 30 questions, 5-6 options each. No right or wrong answers.
- Result page: the recommended track, top work-style traits, and a shareable link
  (`result.html?d=...`) that anyone can open to see the same result — no server involved.
- Track catalog: the four 10th-grade tracks with description, subjects, path after the
  diploma, pros and cons, and a personal 1-5 rating stored per browser.
- Side-by-side comparison of any two tracks.
- Face-off of two tracks (`faceoff.html`): pick the two tracks you are torn between, answer the
  12 most relevant questions, and get a weighted verdict with the strongest deciding answers and
  the winner's sub-track paths.
- A step-by-step guide and a set of short reading articles on choosing a high-school track.
- Site-wide client-side search over tracks, sub-tracks and articles (`search.html`), plus
  draft persistence for the personality test.

## Stack

- HTML, CSS, vanilla JavaScript — no build step, no framework, no external JS libraries
- All content data is embedded in `static/js/core.js` (the JSON files in `data/` are the source
  used to generate it), so the site also works opened directly from disk (`file://`)
- Bootstrap Icons v1.13.2 (vendored in `static/bootstrap-icons/`; each page inlines a small
  sprite of only the icons it uses, built from `static/icons/am-sprite.svg`)
- Vazirmatn web font

## Project layout

```
index.html            landing page
test.html             the 30-question test (renders from data/questions.json)
result.html           decodes ?d= answers and shows the result + share box
majors.html           filter/sort over the four tracks
major.html?slug=…     one track in detail, with personal rating (localStorage)
compare.html?a=…&b=…  side-by-side comparison of two tracks
faceoff.html?a=…&b=…  12-question face-off between two tracks
guide.html            step-by-step guide + FAQs
articles.html         all articles (guide articles + 122 sub-track articles)
article.html?slug=…   a single article
search.html?q=…       client-side site search
404.html              not-found page
static/css/style.css  all styles
static/js/core.js     embedded content data + scoring, face-off, ratings, helpers
static/js/layout.js   mobile menu, scroll reveal, active nav, footer year
static/icons/        am-sprite.svg — Bootstrap Icons sprite inlined into each page
static/bootstrap-icons/  vendored Bootstrap Icons v1.13.2
static/fonts/         Vazirmatn
static/images/        site icon
data/                 content JSON (tracks, questions, articles, sub-track slug map)
```

## Run it

Nothing to install: open `index.html` directly, or serve the directory with any static
server:

```sh
python3 -m http.server 5000
# open http://localhost:5000
```

or host the directory on GitHub Pages / Netlify / nginx / `npx serve`.

## Scoring model

Each answer option carries a weight map in `data/questions.json`: the four clusters
(`riyazi`, `tajrobi`, `ensani`, `fanni`) plus 14 trait dimensions. The test result is the
cluster with the highest total weight; the top three non-zero traits become the "ویژگی‌های بارز"
chips. The face-off ranks the 30 questions by how well they separate the two chosen clusters and
sums the weights for the two clusters only.

## Conventions

- Short lowercase commit messages, one logical change per commit.
- Persian content is proofread carefully (wrong letter endings like -گ / -ی / -ن are common typos).
- No code comments in source files; documentation lives in this README.
- Icons are the vendored Bootstrap Icons: each page inlines the small sprite
  (`static/icons/am-sprite.svg` as a `display:none` SVG at the top of `<body>`), rendered as
  `<svg class="bi"><use href="#name"></use></svg>` so they work even from `file://`.
