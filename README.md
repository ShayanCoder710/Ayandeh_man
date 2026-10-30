# Ayandeh-man (آینده من)

A small web app that helps Iranian students finishing 9th grade pick their high-school track
(math, experimental sciences, humanities, or vocational) for 10th grade. Instead of a long
questionnaire, it runs a short personality-and-interest test, scores the answers against several
academic clusters (math & physics, natural sciences, humanities, social sciences, arts & design) plus
a set of work-style traits (teamwork, income focus, leadership, media, care, field work, ...), and
recommends target majors that fit the person.

## What it does

- Personality and interest test: 30 questions, 5-6 options each. No right or wrong answers.
- Result page: dominant academic cluster, top work-style traits, up to six recommended majors, and a
  shareable link that anyone can open to see the same result.
- Admin panel at `/admin` (login credentials live in `config.py`): total results, cluster
  distribution, most-used traits and recommended majors, plus a table of recent results that an admin
  can open or delete.
- Major catalog: 35 target majors (to pursue after high school) with description, key courses, job
  market, pros and cons, and a 1-5 user rating per visitor (stored per browser).
- Side-by-side comparison of any two majors.
- A step-by-step guide and a set of short reading articles on choosing a high-school track.

## Stack

- Flask (server-rendered Jinja templates, RTL Persian UI, mobile-first)
- MariaDB / MySQL via Flask-SQLAlchemy
- No frontend framework; one CSS file, inline scripts, two fonts (Vazirmatn for UI, JetBrains Mono
  for the share link)
- CSRF protection via Flask-WTF (no form framework)

## Project layout

```
app.py          Flask app, routes, context processors, 404, and the /admin panel
config.py       database URL, secret key, and admin credentials (do not commit casually)
func.py         all data access (safe when the database is unreachable) and scoring
models/         SQLAlchemy table definitions
data/           seed data: majors, questions, articles (JSON)
templates/      Jinja templates (base, pages, partials)
static/         css and fonts
wsgi.py         entry point
```

## Setup

1. Create the database: `CREATE DATABASE ayandeh_man;` and make sure a matching user exists.
2. Put credentials and the database URL in `config.py` (this file is the only place they belong).
3. Install dependencies:

   ```
   python -m venv .venv && .venv/bin/pip install -r requirements.txt
   ```

4. Run:

   ```
   .venv/bin/python wsgi.py
   ```

   The app creates the tables and seeds the catalog on first start. If the database is unreachable at
   startup it still boots in a degraded mode (empty lists, no crash).

## Scoring model

Each answer option carries a small weight map. Cluster weights (5 academic areas) determine the
dominant cluster; trait weights (14 work-style dimensions) produce up to three "notable traits" shown
on the result page. Recommended majors are the top six majors of the dominant cluster, ordered by user
ratings where available.

## Conventions

- Short lowercase commit messages, one logical change per commit.
- Persian content is proofread carefully (wrong letter endings like -گ / -ی / -ن are common typos).
- No code comments in source files; documentation lives in this README.
