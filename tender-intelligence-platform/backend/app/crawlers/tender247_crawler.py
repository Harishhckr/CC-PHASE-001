"""
Tender247 crawler for https://www.tender247.com/
"""
import asyncio
from typing import List, Dict, Any
from playwright.async_api import async_playwright, Page
from loguru import logger

from app.crawlers.base import BaseCrawler
from app.database.models import TenderSource
from app.config import settings, MDM_KEYWORDS


class Tender247Crawler(BaseCrawler):
    """Crawler for Tender247 portal"""

    def __init__(self):
        super().__init__(source=TenderSource.TENDER247)
        self.base_url = "https://www.tender247.com/keyword"
        self.max_pages = settings.TENDER247_MAX_PAGES

    async def crawl(self) -> List[Dict[str, Any]]:
        """Crawl Tender247 tenders using MDM keywords"""
        all_tenders = []

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent=self.get_random_user_agent()
                )
                page = await context.new_page()

                # Crawl for top MDM keywords
                keywords_to_search = [
                    "master data management",
                    "data governance",
                    "material master",
                    "vendor data governance",
                    "cataloguing"
                ]

                for keyword in keywords_to_search:
                    logger.info(f"Searching Tender247 for: {keyword}")

                    try:
                        tenders = await self._crawl_keyword(page, keyword)
                        all_tenders.extend(tenders)
                        await asyncio.sleep(3)
                    except Exception as e:
                        logger.error(f"Error crawling keyword '{keyword}': {e}")
                        continue

                await browser.close()

        except Exception as e:
            logger.error(f"Error in Tender247 crawler: {e}")

        return all_tenders

    async def _crawl_keyword(self, page: Page, keyword: str) -> List[Dict[str, Any]]:
        """Crawl tenders for a specific keyword"""
        tenders = []

        try:
            # Format URL
            keyword_formatted = keyword.replace(" ", "+")
            url = f"{self.base_url}/{keyword_formatted}+tenders"

            logger.debug(f"Accessing: {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)

            # Wait for results
            try:
                await page.wait_for_selector(
                    ".tender-item, .result-item, .tenders-list > div",
                    timeout=10000
                )
            except:
                logger.warning(f"No results found for keyword: {keyword}")
                return tenders

            # Extract tender cards
            tender_cards = await page.query_selector_all(
                ".tender-item, .result-item, .tenders-list > div"
            )

            for card in tender_cards[:20]:  # Limit per keyword
                try:
                    tender_data = await self._extract_tender_data(card)
                    if tender_data:
                        tenders.append(tender_data)
                except Exception as e:
                    logger.error(f"Error extracting tender: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error crawling keyword '{keyword}': {e}")

        return tenders

    async def _extract_tender_data(self, card) -> Dict[str, Any]:
        """Extract tender data from card"""
        try:
            # Extract T247 ID
            id_elem = await card.query_selector(
                "[class*='tender-id'], [class*='t247'], .id-number"
            )
            tender_id = await id_elem.inner_text() if id_elem else ""

            # Extract title
            title_elem = await card.query_selector(
                "h3, h4, .tender-title, .title, strong"
            )
            title = await title_elem.inner_text() if title_elem else ""

            # Extract description
            desc_elem = await card.query_selector(
                ".description, .tender-desc, p"
            )
            description = await desc_elem.inner_text() if desc_elem else ""

            # Extract value
            value_elem = await card.query_selector(
                ".tender-value, .amount, [class*='value']"
            )
            value = await value_elem.inner_text() if value_elem else ""

            # Extract deadline
            deadline_elem = await card.query_selector(
                ".deadline, .due-date, [class*='deadline'], [class*='date']"
            )
            end_date = await deadline_elem.inner_text() if deadline_elem else ""

            # Extract location
            location_elem = await card.query_selector(
                ".location, [class*='location'], [class*='place']"
            )
            location = await location_elem.inner_text() if location_elem else ""

            # Extract buyer/authority
            buyer_elem = await card.query_selector(
                ".authority, .buyer, [class*='buyer'], [class*='org']"
            )
            buyer = await buyer_elem.inner_text() if buyer_elem else ""

            # Extract link
            link_elem = await card.query_selector("a")
            document_link = await link_elem.get_attribute("href") if link_elem else ""

            if document_link and not document_link.startswith("http"):
                document_link = f"https://www.tender247.com{document_link}"

            # Generate ID if not found
            if not tender_id:
                tender_id = f"T247-{hash(title) % 100000000}"

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
                "source": "tender247"
            }

        except Exception as e:
            logger.error(f"Error extracting tender data: {e}")
            return None


async def test_tender247_crawler():
    """Test Tender247 crawler"""
    crawler = Tender247Crawler()
    results = await crawler.run()
    logger.info(f"Crawl results: {results}")


if __name__ == "__main__":
    asyncio.run(test_tender247_crawler())
