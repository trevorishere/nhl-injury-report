# NHL Injuries → Notion (Text-Only) with Free Source

Scrapes the public injury list from PuckPedia and upserts to your Notion DB at 7am America/Los_Angeles. All properties are Text except Name (Title).

**Heads up:** Scraping is fragile and subject to the source site's terms. This runs once daily with a single request. If it breaks, switch DATA_PROVIDER to `csv`.

## Properties (Notion)
Name (Title), Position (Text), Team (Text), Date of injury (Text), Injury status (Text), Return date (Text), Notes (Text), Player ID (Text)

## Setup
- Repo Secrets: NOTION_TOKEN, NOTION_DATABASE_ID
- Optional Variable: TIMEZONE=America/Los_Angeles
- `.env`: DATA_PROVIDER=puckpedia

## Run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
IGNORE_TIME_WINDOW=1 python -m src.main
```

## Attribution
Data derived from https://puckpedia.com/injuries
