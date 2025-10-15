
from typing import List, Dict, Tuple
import time
import requests
from bs4 import BeautifulSoup
from .base import InjuryProvider

LIST_URL = "https://puckpedia.com/injuries"
BASE = "https://puckpedia.com"

def clean_text(s: str) -> str:
    return " ".join((s or "").replace("\xa0"," ").split())[:200]

def extract_team_position_from_profile(soup: BeautifulSoup) -> Tuple[str, str]:
    team = ""
    pos = ""
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        parts = [p.strip() for p in og_title["content"].split("|")]
        if len(parts) >= 2:
            team = parts[1].strip()
        if len(parts) >= 3:
            pos = parts[2].strip()
    for lbl in soup.find_all(["strong","b","th"]):
        txt = lbl.get_text(" ", strip=True)
        if not txt:
            continue
        low = txt.lower()
        if "team" in low and not team:
            v = lbl.parent.get_text(" ", strip=True) if lbl.parent else ""
            v = v.split(":",1)[-1] if ":" in v else v.replace(txt,"")
            team = clean_text(v)
        if "position" in low and not pos:
            v = lbl.parent.get_text(" ", strip=True) if lbl.parent else ""
            v = v.split(":",1)[-1] if ":" in v else v.replace(txt,"")
            pos = clean_text(v)
    return team, pos

class PuckPediaPlusProvider(InjuryProvider):
    def fetch(self) -> List[Dict]:
        headers = {"User-Agent": "NHL-Injury-Tracker/1.0 (+respectful; 1 req/day; contact if needed)"}
        r = requests.get(LIST_URL, headers=headers, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")

        items: List[Dict] = []
        container = soup.find(id="block-puckpedia-content") or soup
        for a in container.select("a[href^='/player/'], a[href^='/injuries/'], a[href^='/name/'], a[href^='/players/']"):
            name = clean_text(a.get_text())
            if not name or "," not in name:
                continue
            ctx = clean_text(a.parent.get_text(" ", strip=True) if a.parent else "")
            status = ""
            for token in ["Day to Day","Week to Week","Month to Month","IR","LTIR","OUT"]:
                if token in ctx and len(token) > len(status):
                    status = token
            reason = ""
            for clue in ["Upper Body","Lower Body","Undisclosed","Groin","Hand","Knee","Back","Hip","Wrist","Shoulder","Concussion","Personal","Suspension"]:
                if clue in ctx:
                    tail = ctx.split(status)[-1] if status and status in ctx else ctx
                    for prefix in ["OUT","IR","LTIR"]:
                        if tail.startswith(prefix):
                            tail = tail[len(prefix):].strip()
                    reason = clean_text(tail)
                    break

            href = a.get("href") or ""
            if href and href.startswith("/"):
                href = BASE + href

            team = ""
            pos = ""
            if href:
                try:
                    time.sleep(0.5)
                    pr = requests.get(href, headers=headers, timeout=20)
                    if pr.ok:
                        psoup = BeautifulSoup(pr.text, "lxml")
                        team, pos = extract_team_position_from_profile(psoup)
                except requests.RequestException:
                    pass

            items.append({
                "name": name,
                "position": pos,
                "team": team,
                "date_of_injury": "",
                "injury_status": status,
                "return_date": "",
                "notes": reason,
                "player_id": "",
            })

        seen = {}
        for it in items:
            key = (it["name"].lower(), it["injury_status"], it["notes"])
            if key not in seen:
                seen[key] = it
            else:
                cur = seen[key]
                if not cur.get("team") and it.get("team"):
                    cur["team"] = it["team"]
                if not cur.get("position") and it.get("position"):
                    cur["position"] = it["position"]
        return list(seen.values())
