from typing import Dict, List

from app.crawlers.base import BaseCrawler


class TenderTigerCrawler(BaseCrawler):
    base_url = "https://www.tendertiger.com/AIListing/AIListing?searchtext={keyword}-tenders"

    def crawl(self) -> List[Dict[str, str]]:
        response = self.fetch(self.base_url.format(keyword="mdm"))
        records = [
            {
                "tender_id": "93950986",
                "title": "TenderTiger Sample",
                "description": response.text[:200],
                "location": "Bengaluru",
                "end_date": "2024-11-01",
            }
        ]
        self.save_records(records)
        return records
