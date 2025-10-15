
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
from .base import InjuryProvider

URL = "https://puckpedia.com/injuries"

class PuckPediaProvider(InjuryProvider):
    def fetch(self) -> List[Dict]:
        r = requests.get(URL, headers={"User-Agent": "NHL-Injury-Tracker/1.0"}, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")

        items: List[Dict] = []
        container = soup.find(id="block-puckpedia-content") or soup
        for a in container.select("a"):
            name = (a.get_text(strip=True) or "")
            if not name or "," not in name:
                continue
            ctx = a.parent.get_text(" ", strip=True) if a.parent else ""
            status = ""
            for token in ["Day to Day", "Week to Week", "Month to Month", "IR", "LTIR", "OUT"]:
                if token in ctx and len(token) > len(status):
                    status = token
            reason = ""
            for clue in ["Upper Body","Lower Body","Undisclosed","Groin","Hand","Knee","Back","Hip","Wrist","Shoulder","Concussion","Personal","Suspension"]:
                if clue in ctx:
                    tail = ctx.split(status)[-1] if status else ctx
                    for prefix in ["OUT", "IR", "LTIR"]:
                        if tail.startswith(prefix):
                            tail = tail[len(prefix):].strip()
                    reason = tail[:200].strip()
                    break
            items.append({
                "name": name,
                "position": "",
                "team": "",
                "date_of_injury": "",
                "injury_status": status,
                "return_date": "",
                "notes": reason,
                "player_id": "",
            })
        seen = set()
        out: List[Dict] = []
        for it in items:
            key = (it["name"].lower(), it["injury_status"], it["notes"])
            if key in seen:
                continue
            seen.add(key)
            out.append(it)
        return out
