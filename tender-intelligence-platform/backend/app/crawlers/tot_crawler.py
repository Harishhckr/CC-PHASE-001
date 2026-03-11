from typing import Dict, List

from app.crawlers.base import BaseCrawler


class TenderOnTimeCrawler(BaseCrawler):
    base_url = "https://www.tenderontime.com"

    def crawl(self) -> List[Dict[str, str]]:
        response = self.fetch(self.base_url)
        records = [
            {
                "tender_id": "TOT-001",
                "title": "TenderOnTime Sample",
                "description": response.text[:200],
                "end_date": "2024-11-30",
            }
        ]
        self.save_records(records)
        return records
