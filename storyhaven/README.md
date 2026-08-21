# Storyhaven

A Django + Django REST Framework backend skeleton for a story-hosting webapp
(think Wattpad/AO3 hybrid): writers publish serialized stories, readers
browse, follow, bookmark, and comment.

This is the MVP scaffold from the project plan — a Python-based rewrite of
the original Node/React plan.

## Stack

- **Backend:** Django 5/6 + Django REST Framework
- **Database:** SQLite for local dev (swap `DATABASES` for Postgres in
  production)
- **Media:** Pillow for cover image uploads

## Data model

`User -> Story -> Chapter -> Comment`, plus `Tag` (M2M with Story), `Like`
(per chapter), `Follow` (user-to-user or user-to-story), and `Bookmark`
(per user/story, tracks last read chapter).

## Getting started

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

- Admin site: `/admin/`
- API root: `/api/` (stories, chapters, comments, likes, follows, bookmarks,
  tags — all as DRF `ModelViewSet`s registered on a `DefaultRouter`)
- Browsable API login: `/api-auth/`

## Running tests

```bash
python manage.py test
```

## Notes / next steps

- Swap SQLite for PostgreSQL and wire up `DATABASE_URL` via an env var for
  deployment.
- Add Celery + Redis for background jobs (email/notifications) per the
  project roadmap.
- Add richer search (Postgres full-text or Meilisearch) once the MVP is
  live.
