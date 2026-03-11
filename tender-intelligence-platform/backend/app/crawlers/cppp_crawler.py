from typing import Dict, List

from app.crawlers.base import BaseCrawler


class CpppCrawler(BaseCrawler):
    base_url = "https://eprocure.gov.in/cppp"

    def crawl(self) -> List[Dict[str, str]]:
        response = self.fetch(self.base_url)
        records = [
            {
                "tender_id": "CPPP-001",
                "title": "CPPP Tender",
                "description": response.text[:200],
                "end_date": "2024-12-15",
            }
        ]
        self.save_records(records)
        return records
