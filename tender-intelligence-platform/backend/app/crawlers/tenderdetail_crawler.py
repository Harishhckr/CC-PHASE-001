"""
TenderDetail crawler for https://www.tenderdetail.com/
"""
import asyncio
import requests
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from loguru import logger

from app.crawlers.base import BaseCrawler
from app.database.models import TenderSource
from app.config import settings


class TenderDetailCrawler(BaseCrawler):
    """Crawler for TenderDetail portal using requests + BeautifulSoup"""

    def __init__(self):
        super().__init__(source=TenderSource.TENDERDETAIL)
        self.base_url = "https://www.tenderdetail.com/Indian-tender"
        self.max_pages = settings.TENDERDETAIL_MAX_PAGES
        self.session = requests.Session()

    async def crawl(self) -> List[Dict[str, Any]]:
        """Crawl TenderDetail tenders"""
        all_tenders = []

        try:
            # Search keywords
            keywords = [
                "master-data-management",
                "data-governance",
                "material-master",
                "cataloguing"
            ]

            for keyword in keywords:
                logger.info(f"Searching TenderDetail for: {keyword}")

                try:
                    tenders = await self._crawl_keyword(keyword)
                    all_tenders.extend(tenders)
                    await asyncio.sleep(2)
                except Exception as e:
                    logger.error(f"Error crawling keyword '{keyword}': {e}")
                    continue

        except Exception as e:
            logger.error(f"Error in TenderDetail crawler: {e}")

        return all_tenders

    async def _crawl_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """Crawl tenders for a keyword"""
        tenders = []

        try:
            url = f"{self.base_url}/{keyword}-tenders"
            headers = {
                "User-Agent": self.get_random_user_agent(),
                "Accept": "text/html,application/xhtml+xml",
            }

            response = self.session.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Find tender listings
            tender_items = soup.find_all(
                ["div", "tr"],
                class_=lambda x: x and any(
                    term in x.lower() for term in ["tender", "result", "item", "row"]
                )
            )

            for item in tender_items[:20]:  # Limit per keyword
                try:
                    tender_data = self._extract_tender_data(item)
                    if tender_data:
                        tenders.append(tender_data)
                except Exception as e:
                    logger.error(f"Error extracting tender: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error crawling keyword '{keyword}': {e}")

        return tenders

    def _extract_tender_data(self, item) -> Dict[str, Any]:
        """Extract tender data from HTML element"""
        try:
            # Extract tender ID
            id_elem = item.find(
                ["span", "div", "td"],
                class_=lambda x: x and "id" in x.lower()
            )
            tender_id = id_elem.get_text(strip=True) if id_elem else ""

            # Extract title
            title_elem = item.find(["h3", "h4", "a", "strong"])
            title = title_elem.get_text(strip=True) if title_elem else ""

            # Extract description
            desc_elem = item.find(
                ["p", "div"],
                class_=lambda x: x and "desc" in x.lower()
            )
            description = desc_elem.get_text(strip=True) if desc_elem else ""

            # Extract authority/buyer
            buyer_elem = item.find(
                ["span", "div"],
                class_=lambda x: x and any(
                    term in x.lower() for term in ["authority", "buyer", "org"]
                )
            )
            buyer = buyer_elem.get_text(strip=True) if buyer_elem else ""

            # Extract location
            location_elem = item.find(
                ["span", "div"],
                class_=lambda x: x and "location" in x.lower()
            )
            location = location_elem.get_text(strip=True) if location_elem else ""

            # Extract due date
            date_elem = item.find(
                ["span", "div"],
                class_=lambda x: x and any(
                    term in x.lower() for term in ["date", "deadline", "due"]
                )
            )
            end_date = date_elem.get_text(strip=True) if date_elem else ""

            # Extract value
            value_elem = item.find(
                ["span", "div"],
                class_=lambda x: x and "value" in x.lower()
            )
            value = value_elem.get_text(strip=True) if value_elem else ""

            # Extract link
            link_elem = item.find("a", href=True)
            document_link = link_elem["href"] if link_elem else ""

            if document_link and not document_link.startswith("http"):
                document_link = f"https://www.tenderdetail.com{document_link}"

            # Generate ID if not found
            if not tender_id:
                # Try to extract numeric ID from link or text
                import re
                id_match = re.search(r'\d{5,}', str(item))
                tender_id = id_match.group(0) if id_match else f"TD-{hash(title) % 100000000}"

            if not title:
                return None

            return {
                "tender_id": tender_id,
                "title": title,
                "description": description,
                "end_date": end_date,
                "buyer": buyer,
                "value": value,
                "location": location,
                "document_link": document_link,
                "source": "tenderdetail"
            }

        except Exception as e:
            logger.error(f"Error extracting tender data: {e}")
            return None


async def test_tenderdetail_crawler():
    """Test TenderDetail crawler"""
    crawler = TenderDetailCrawler()
    results = await crawler.run()
    logger.info(f"Crawl results: {results}")


if __name__ == "__main__":
    asyncio.run(test_tenderdetail_crawler())
