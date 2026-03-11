from typing import Dict, List

from app.crawlers.base import BaseCrawler


class GemCrawler(BaseCrawler):
    base_url = "https://bidplus.gem.gov.in/all-bids"

    def crawl(self) -> List[Dict[str, str]]:
        records = []
        for page in range(1, 3):
            response = self.fetch(self.base_url, params={"page": page})
            records.append(
                {
                    "tender_id": f"GEM-{page}",
                    "title": "Sample GEM Tender",
                    "description": response.text[:200],
                    "end_date": "2024-12-31",
                }
            )
        self.save_records(records)
        return records
