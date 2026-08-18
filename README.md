# TrailLog

A personal hiking & trail journal. Log every trail you've hiked — distance, elevation
gain, difficulty, duration, notes, a 1-5 rating — and TrailLog turns your log into a
lifetime stats dashboard and a rail of milestone badges.

**Live demo:** https://traillog.onrender.com

## Features

- **Trail journal** — log hikes with trail name, location, date, distance, elevation
  gain, duration, difficulty (Easy/Moderate/Hard/Strenuous), a 5-star rating, and notes.
- **Lifetime stats dashboard** — total miles, total elevation climbed, total hikes, and
  miles hiked this year, all computed live from your log (no counters to keep in sync).
- **Milestone badges** — automatic badges for mileage (10/25/50/100/250/500 mi),
  elevation (5k/10k/25k/50k/100k ft) and hike-count thresholds.
- **Search & filter** — filter your hike list by difficulty or year, or search by trail
  name.
- **Per-user accounts** — standard Django auth; every hiker only ever sees their own
  log (verified with tests — another user's hike 404s, it doesn't 403).
- **No JS build step** — server-rendered Django templates with one small
  progressive-enhancement `<script>` (a delete confirmation); everything else works
  with JavaScript off.
- **100% original artwork** — every icon, the mountain-ridge hero, the compass-rose
  logo, and the per-difficulty elevation-profile sparklines are hand-written inline SVG.
  No icon library, no stock photography.

## Tech Stack

- **Backend:** Django 6.1, Python 3.12
- **Database:** SQLite (see note below)
- **Static files:** WhiteNoise (`CompressedManifestStaticFilesStorage` in production)
- **Server:** Gunicorn
- **Frontend:** Server-rendered Django templates, hand-written CSS (no framework, no
  build step), Google Fonts (Big Shoulders Display + Nunito Sans)
- **Hosting:** Render (single Web Service)

## Project Structure

```
traillog/
├── core/                 # Django project: settings, root urls, wsgi
├── trails/                # Main app
│   ├── models.py          # Hike model + user_stats() aggregate helper
│   ├── views.py            # Landing, auth, dashboard, hike CRUD
│   ├── forms.py             # SignUpForm, HikeForm
│   ├── urls.py
│   ├── admin.py
│   ├── tests.py             # 15 tests: auth, CRUD, per-user isolation, stats/badges
│   └── templates/trails/    # Page templates + reusable SVG partials
├── templates/              # base.html, 404/500, robots.txt, sitemap.xml
├── static/css/style.css    # Hand-written design system
├── static/img/favicon.svg
├── requirements.txt
├── build.sh                 # Render build command
└── manage.py
```

## Persistence caveat

This deploys with SQLite on Render's free tier, which means the database lives on
**ephemeral disk** — every redeploy resets it to whatever is (or isn't) committed. This
is fine for a demo; a real production deployment of an app people store their trail
history in should use Render's managed Postgres (or another persistent database)
instead.

## Testing

```bash
python manage.py test trails
```

15 tests cover signup/login, hike CRUD, per-user isolation (another user's hike returns
404, not 403), and the stats/badge aggregation logic (empty state, multi-hike totals,
per-user isolation of stats, year-scoped totals).

See [instructions.md](instructions.md) for local setup.
