import os
from typing import Dict, List, Optional
from notion_client import Client

def notion_client() -> Client:
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        raise RuntimeError("NOTION_TOKEN not set")
    return Client(auth=token)

def build_properties(item: Dict) -> Dict:
    def rt(v: str):
        return {"rich_text": [{"text": {"content": (v or "")[:1999]}}]} if v else {"rich_text": []}
    def title(v: str):
        return {"title": [{"text": {"content": (v or "")[:1999]}}]}
    return {
        "Name": title(item.get("name","")),
        "Position": rt(item.get("position","")),
        "Team": rt(item.get("team","")),
        "Date of injury": rt(item.get("date_of_injury","")),
        "Injury status": rt(item.get("injury_status","")),
        "Return date": rt(item.get("return_date","")),
        "Notes": rt(item.get("notes","")),
        "Player ID": rt(item.get("player_id","")),
    }

def page_key(item: Dict) -> str:
    pid = (item.get("player_id") or "").strip()
    if pid:
        return f"id:{pid}"
    return f"name_team:{(item.get('name') or '').strip().lower()}|{(item.get('team') or '').strip().lower()}"

def index_existing(db_id: str, client: Optional[Client] = None) -> Dict[str, str]:
    client = client or notion_client()
    results = {}
    start_cursor = None
    while True:
        resp = client.databases.query(database_id=db_id, start_cursor=start_cursor) if start_cursor else client.databases.query(database_id=db_id)
        for page in resp.get("results", []):
            props = page.get("properties", {})
            pid = ""
            if "Player ID" in props:
                rich = props["Player ID"].get("rich_text", [])
                if rich and "text" in rich[0] and "content" in rich[0]["text"]:
                    pid = (rich[0]["text"]["content"] or "").strip()
            name = ""
            if "Name" in props and props["Name"].get("title"):
                name = props["Name"]["title"][0].get("plain_text"," ").strip().lower()
            team = ""
            if "Team" in props and props["Team"].get("rich_text"):
                team = props["Team"]["rich_text"][0].get("plain_text"," ").strip().lower()
            key = f"id:{pid}" if pid else f"name_team:{name}|{team}"
            results[key] = page["id"]
        if not resp.get("has_more"):
            break
        start_cursor = resp.get("next_cursor")
    return results

def upsert_items(db_id: str, items: List[Dict], client: Optional[Client] = None) -> Dict[str, int]:
    client = client or notion_client()
    existing = index_existing(db_id, client)
    created = 0
    updated = 0
    for item in items:
        props = build_properties(item)
        key = page_key(item)
        page_id = existing.get(key)
        if page_id:
            client.pages.update(page_id=page_id, properties=props)
            updated += 1
        else:
            client.pages.create(parent={"database_id": db_id}, properties=props)
            created += 1
    return {"created": created, "updated": updated}
