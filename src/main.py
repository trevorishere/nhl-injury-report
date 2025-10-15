import os
from datetime import datetime
import pytz
from dotenv import load_dotenv

from src.providers.csv_provider import CSVProvider
from src.providers.puckpedia_plus_provider import PuckPediaPlusProvider
from src.notion_updater import upsert_items

def is_right_hour() -> bool:
    tz = os.environ.get("TIMEZONE", "America/Los_Angeles")
    now = datetime.now(pytz.timezone(tz))
    return now.hour == 7

def get_provider():
    kind = os.environ.get("DATA_PROVIDER", "puckpedia_plus").lower()
    if kind == "csv":
        csv_path = os.environ.get("CSV_PATH", "data/sample_injuries.csv")
        return CSVProvider(csv_path)
    if kind in ("puckpedia", "puckpedia_plus"):
        return PuckPediaPlusProvider()
    raise RuntimeError(f"Unknown DATA_PROVIDER: {kind}")

def main():
    load_dotenv()
    if not is_right_hour() and os.environ.get("IGNORE_TIME_WINDOW","").lower() not in ("1","true","yes"):
        print("Not 7am local; exiting.")
        return
    notion_db = os.environ.get("NOTION_DATABASE_ID")
    if not notion_db:
        raise RuntimeError("NOTION_DATABASE_ID not set")
    items = get_provider().fetch()
    cleaned = [r for r in items if r.get("name")]
    summary = upsert_items(notion_db, cleaned)
    print(f"Upsert complete: {summary}")

if __name__ == "__main__":
    main()
