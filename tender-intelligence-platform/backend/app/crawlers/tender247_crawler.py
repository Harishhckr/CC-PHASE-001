from typing import Dict, List

from app.crawlers.base import BaseCrawler


class Tender247Crawler(BaseCrawler):
    base_url = "https://www.tender247.com/keyword/{keyword}+tenders"

    def crawl(self) -> List[Dict[str, str]]:
        response = self.fetch(self.base_url.format(keyword="mdm"))
        records = [
            {
                "tender_id": "93950960",
                "title": "Tender247 Sample",
                "description": response.text[:200],
                "location": "Mumbai",
                "end_date": "2024-10-20",
            }
        ]
        self.save_records(records)
        return records
