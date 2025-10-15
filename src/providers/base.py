from typing import List, Dict

class InjuryProvider:
    def fetch(self) -> List[Dict]:
        raise NotImplementedError
