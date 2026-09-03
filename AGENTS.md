# Base44 Dev Environment

## Stack
- Django 6.0.7 web app (`trading_platform` project), SQLite DB (`trading_system.db`), served by `manage.py runserver` (live-reload dev server).
- The dashboard app (`dashboard/`) renders the single page at `/` (`dashboard/templates/dashboard/index.html`).
- A background market-simulation thread starts from `dashboard/apps.py` `ready()` only when `RUN_MAIN=true` (set automatically by runserver's autoreload child). It writes XAU/USD candles + trade ledger entries to SQLite every ~5s. It uses the Twelve Data API only if a real key is set in `apps.py`; otherwise it falls back to a random-walk simulation — **no external credentials are required to boot**.

## Running
- `docker compose -f docker-compose.base44.yml up -d` — installs deps, runs migrations, creates the admin superuser, collects static files, then starts runserver on port 3000.
- `ALLOWED_HOSTS=["*"]` in DEBUG, so the preview's external hostname works without config.
- Admin: `/admin/` (user `admin` / `Pass12345`, created by `create_admin.py`).

## Notes / Quirks
- The committed `trading_system.db` already contains Django tables + sample data and migrations through `dashboard/0002`. Migration `0003_add_action_to_ledgerhistory` is applied on boot (adds nullable `action` to `LedgerHistory`).
- `run.py` and `main.py` are a separate Termux/CLI shell (raw sqlite, different `account_state` schema) — NOT the web entry point. The web app uses the `dashboard_*` Django tables, not the legacy `account_state`/`ledger_history` tables.
- No external-service secrets are needed; the app simulates market data locally.
