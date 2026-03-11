from typing import Dict, List

from app.crawlers.base import BaseCrawler


class MaharashtraCrawler(BaseCrawler):
    base_url = "https://mahatenders.gov.in"

    def crawl(self) -> List[Dict[str, str]]:
        response = self.fetch(self.base_url)
        records = [
            {
                "tender_id": "MH-001",
                "title": "Maharashtra Tender",
                "description": response.text[:200],
                "location": "Mumbai",
                "end_date": "2024-10-05",
            }
        ]
        self.save_records(records)
        return records
