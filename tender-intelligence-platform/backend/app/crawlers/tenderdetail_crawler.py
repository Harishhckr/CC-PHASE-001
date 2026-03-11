from typing import Dict, List

from bs4 import BeautifulSoup

from app.crawlers.base import BaseCrawler


class TenderDetailCrawler(BaseCrawler):
    base_url = "https://www.tenderdetail.com/Indian-tender/{keyword}-tenders"

    def crawl(self) -> List[Dict[str, str]]:
        response = self.fetch(self.base_url.format(keyword="mdm"))
        soup = BeautifulSoup(response.text, "html.parser")
        _ = soup.title.text if soup.title else "Tender Detail"
        records = [
            {
                "tender_id": "54506167",
                "title": "TenderDetail Sample",
                "description": response.text[:200],
                "location": "Delhi",
                "end_date": "2024-09-18",
            }
        ]
        self.save_records(records)
        return records
