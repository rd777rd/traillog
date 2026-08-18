# TrailLog — Planning

**Concept:** A personal hiking & trail journal. Hikers log every trail they've completed
(distance, elevation gain, difficulty, duration, notes, rating), and the app turns that log
into a lifetime stats dashboard (total miles, total elevation climbed, hikes-per-year) plus
simple milestone badges. Django-only (server-rendered templates, no JS build step), deployed
as a single Render Web Service — the least-represented build pattern in the pipeline so far
(1 of 8 prior sites), chosen deliberately for variety over another React+Django build.

## 1. Design Plan

- **Palette:** forest green `#2D4A34` (primary), trail-dust tan `#D8C9A3` (secondary/bg),
  cream `#F7F3EA` (page bg), charcoal `#2A2A28` (text), sunset ember `#D97B3F` (accent/CTA).
- **Type:** Google Fonts — `Big Shoulders Display` (condensed, tall — headings, stat numbers)
  + `Nunito Sans` (body). Neither font has been used elsewhere in this pipeline yet.
- **Art:** 100% original inline SVG — layered mountain ridge hero, a hand-drawn compass rose
  mark used as the site logo, a topographic contour-line background texture, per-hike elevation
  "profile" mini-chart generated from each hike's stored elevation number (not a real GPS
  trace — a stylized triangular sparkline), and badge medallions for milestones. No icon
  library, no stock photography.
- **Layout:** public marketing landing page (logged-out) selling the idea of a trail journal;
  authenticated dashboard with stat tiles + badge rail + recent hikes; hike list with
  difficulty/year filters; add/edit hike form; hike detail page.

## 2. SEO Plan

- Server-rendered HTML (no client JS required for content) — inherently crawlable.
- Per-page `<title>`/meta description via a small `{% block meta_description %}`.
- Semantic headings, `alt` text on all inline SVG via `<title>` tags / `role="img"` +
  `aria-label`.
- `robots.txt` + `sitemap.xml` (static, hand-written — small fixed route set).
- Open Graph + Twitter card tags on the landing page (static SVG-derived PNG not needed —
  use a themed OG description; no external image generation available offline).
- Semantic URL slugs are not needed (this is a personal-use tool, not public trail content),
  so no per-trail public SEO pages — landing page is the only page search engines should
  meaningfully index; `noindex` on authenticated app pages via `<meta name="robots">`.

## 3. Code Plan

- Django project `core`, single app `trails`.
- Models: `Hike` (owner FK to `User`, trail_name, location, date_hiked, distance_miles
  `DecimalField`, elevation_gain_ft `PositiveIntegerField`, duration_minutes, difficulty
  choice field, rating 1-5, notes, created_at). All stats (total miles, total elevation,
  hikes this year, milestone badges) computed on read via a query aggregate helper — no
  denormalized counters to keep in sync, matching the "compute on read" pattern proven on
  streakkeeper but applied to a genuinely different domain (threshold badges, not streaks).
- Auth: Django's built-in `User` + session auth; signup/login/logout views with plain
  `<form>` POSTs (no JS required, matches "works with JS off" ethos of the rest of the
  pipeline).
- Per-user isolation: every hike queryset filtered by `request.user`; a hike detail/edit
  view for another user's hike returns 404 (not 403) — same pattern proven on streakkeeper.
- No JS build step at all (plain `<script>` tags for the one bit of progressive-enhancement
  JS: client-side confirm on delete). WhiteNoise serves `/static/` normally — this build has
  **no React frontend**, so the `/assets` WHITENOISE_ROOT class of bug documented in memory
  does not apply here; still keep `STORAGES["staticfiles"]` conditional on `DEBUG`
  (`StaticFilesStorage` in DEBUG, `CompressedManifestStaticFilesStorage` in production) per
  the streakkeeper lesson, since `collectstatic` only runs in the Render build step.
- `DJANGO_SECRET_KEY` / `DJANGO_DEBUG` from env vars, `DEBUG` parsed as a real bool (never a
  bare string — this is the exact bug found and fixed on the real romsites production site).
- `PYTHON_VERSION` pinned to `3.12.8` on Render (Django 5.1 requires Python ≥3.10; 3.12.8 is
  a safe, already-proven pin from the driftwood-sauna-co build).

## 4. Audit Plan

- Full Django test suite: signup/login/logout, hike CRUD, per-user isolation (404 not 403),
  stats aggregation correctness (miles/elevation/hikes-this-year), badge threshold logic.
- Real `python manage.py runserver` + `curl -e <referer>` smoke test of POST endpoints
  against `DEBUG=False` locally before deploying (CSRF Referer-check lesson).
- Mobile-overflow DOM-clone audit (required) against the **live deployed URL** post-deploy,
  every route incl. logged-in dashboard/hike-list/add-hike views.
- Post-deploy `curl -I` of static asset URLs to confirm `Content-Type` is correct (cheap
  sanity check even though this build has no SPA catch-all to make it silently fail).

## 5. Deployment Plan

- GitHub: new public repo `traillog` under `rd777rd` (confirmed no name collision).
- Render: single Web Service, runtime `python`, `buildCommand: "bash build.sh"`
  (`pip install`, `collectstatic`, `migrate`), `startCommand:
  "gunicorn core.wsgi:application --bind 0.0.0.0:$PORT"`, plan `free`, region `oregon`,
  env vars: `DJANGO_SECRET_KEY` (locally generated), `DJANGO_DEBUG=False`,
  `PYTHON_VERSION=3.12.8`.
- Poll `get_deploy` until `status: "live"`; verify with a real page load + curl.
- Zip as `traillog-vP1.zip` into `Desktop/Agents Websites/`, delete the unzipped working
  copy afterward.
