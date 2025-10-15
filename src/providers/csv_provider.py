from typing import List, Dict
import pandas as pd
from .base import InjuryProvider

class CSVProvider(InjuryProvider):
    def __init__(self, csv_path: str):
        self.csv_path = csv_path

    def fetch(self) -> List[Dict]:
        df = pd.read_csv(self.csv_path, dtype=str).fillna("")
        expected = ["name","position","team","date_of_injury","injury_status","return_date","notes","player_id"]
        for col in expected:
            if col not in df.columns:
                df[col] = ""
            df[col] = df[col].astype(str).str.strip()
        return df[expected].to_dict(orient="records")
