# Mad Perfume — Backend

Django 6 + DRF, managed with [uv](https://docs.astral.sh/uv/).

```bash
cp .env.example .env
uv sync
uv run python manage.py migrate
uv run python manage.py runserver
uv run python manage.py test --settings=core.settings.test
```

- Health: `GET /api/v1/health/`
- API docs (for the mobile app): `/api/docs/`
- Django admin: `/admin/`

Settings: `core/settings/{base,dev,prod,test}.py`. Feature apps live under `Apps/`.
