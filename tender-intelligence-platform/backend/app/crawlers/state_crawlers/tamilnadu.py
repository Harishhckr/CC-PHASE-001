from typing import Dict, List

from app.crawlers.base import BaseCrawler


class TamilNaduCrawler(BaseCrawler):
    base_url = "https://tntenders.gov.in"

    def crawl(self) -> List[Dict[str, str]]:
        response = self.fetch(self.base_url)
        records = [
            {
                "tender_id": "TN-001",
                "title": "Tamil Nadu Tender",
                "description": response.text[:200],
                "location": "Chennai",
                "end_date": "2024-09-30",
            }
        ]
        self.save_records(records)
        return records
