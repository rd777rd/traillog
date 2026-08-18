# TrailLog — Local Development Setup

## Prerequisites

- Python 3.12+ (Django 6.1 requires Python ≥ 3.12)

## Setup

```bash
git clone https://github.com/rd777rd/traillog.git
cd traillog
python -m venv venv
```

Activate the virtual environment:

```bash
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

Install dependencies and set up the database:

```bash
pip install -r requirements.txt
python manage.py migrate
```

Run the dev server:

```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000 — sign up for an account and start logging hikes.

## Running tests

```bash
python manage.py test trails
```

## Environment variables (optional for local dev)

| Variable | Default | Purpose |
|---|---|---|
| `DJANGO_SECRET_KEY` | a dev-only insecure key | Django's `SECRET_KEY` |
| `DJANGO_DEBUG` | `True` locally | Set to `False` in production |

Locally, you can skip both — `DEBUG` defaults to `True` and a fallback secret key is
used automatically. In production (Render), both are set as real environment variables;
`DJANGO_DEBUG=False` also turns on HTTPS redirect, secure cookies, and HSTS.

## Creating an admin user

```bash
python manage.py createsuperuser
```

Then visit `/admin/` to manage `Hike` records directly.
