# Agent notes

## Running this app (dev / sandbox)

```
docker compose -f docker-compose.base44.yml up -d --build
```

- Django project, served on host port **3000** by the auto-reloading dev server, so
  source edits are picked up without a rebuild. Deps are baked into the image
  (`.base44/Dockerfile`); rebuild only when `requirements.txt` changes.
- Migrations run automatically on container start (`dashboard` app owns the schema).
- The database is the committed SQLite file `trading_system.db` (not in `.gitignore`),
  so schema changes show up as a modified file in git.
- Sanity checks: `curl localhost:3000/` (dashboard HTML) and
  `curl 'localhost:3000/?format=json'` (telemetry payload consumed by the page's
  polling loop).

## Non-obvious behaviour

- `dashboard/apps.py` starts a background "market clock" that writes candles every
  5s. It only runs when `RUN_MAIN == "true"`, i.e. under the reloading dev server —
  it does **not** run under `runserver --noreload` or gunicorn. That is why the
  charts only move in development.
- The page polls `/?format=json` every 2s and reads `balance`, `cushion`,
  `margin_call`, `chart_labels`, `chart_data` and `table_rows`. Dropping or renaming
  a key there makes the client-side refresh abort silently (the data stays at its
  server-rendered values), so keep `dashboard/views.py`'s JSON payload in sync with
  the template script.
- Known gap (pre-existing): the "Inject Position Override" button fetches
  `/?action=trade`, which no view implements, so the click does nothing.

## Build / deploy paths that previously failed

- `render.yaml` is the deploy blueprint: it must stay valid YAML. A duplicated,
  mis-indented `buildCommand` key made the whole file unparseable, so the service
  failed to start before any code ran.
- `requirements.txt` pins Django 6.0.x, which requires **Python >= 3.12**; the CI
  workflow matrix must not include older interpreters or `pip install` fails.
