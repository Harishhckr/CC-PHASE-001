"""
GEM BidPlus crawler for https://bidplus.gem.gov.in/all-bids
"""
import asyncio
from typing import List, Dict, Any
from playwright.async_api import async_playwright, Page
from loguru import logger

from app.crawlers.base import BaseCrawler
from app.database.models import TenderSource
from app.config import settings


class GEMCrawler(BaseCrawler):
    """Crawler for GEM BidPlus portal"""

    def __init__(self):
        super().__init__(source=TenderSource.GEM)
        self.base_url = "https://bidplus.gem.gov.in/all-bids"
        self.max_pages = settings.GEM_MAX_PAGES

    async def crawl(self) -> List[Dict[str, Any]]:
        """Crawl GEM BidPlus tenders"""
        tenders = []

        try:
            async with async_playwright() as p:
                # Launch browser
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent=self.get_random_user_agent()
                )
                page = await context.new_page()

                # Crawl multiple pages
                for page_num in range(1, self.max_pages + 1):
                    logger.info(f"Crawling GEM page {page_num}/{self.max_pages}")

                    try:
                        page_tenders = await self._crawl_page(page, page_num)
                        tenders.extend(page_tenders)

                        # Break if no tenders found
                        if not page_tenders:
                            logger.info(f"No tenders found on page {page_num}, stopping")
                            break

                        # Small delay between pages
                        await asyncio.sleep(2)

                    except Exception as e:
                        logger.error(f"Error crawling GEM page {page_num}: {e}")
                        continue

                await browser.close()

        except Exception as e:
            logger.error(f"Error in GEM crawler: {e}")

        return tenders

    async def _crawl_page(self, page: Page, page_num: int) -> List[Dict[str, Any]]:
        """Crawl a single page of GEM tenders"""
        tenders = []

        try:
            # Navigate to page
            url = f"{self.base_url}?page={page_num}"
            await page.goto(url, wait_until="networkidle", timeout=30000)

            # Wait for tender cards to load
            await page.wait_for_selector(".bid-card, .tender-card, .search-result-item", timeout=10000)

            # Extract tender data
            tender_cards = await page.query_selector_all(".bid-card, .tender-card, .search-result-item")

            for card in tender_cards:
                try:
                    tender_data = await self._extract_tender_data(card)
                    if tender_data:
                        tenders.append(tender_data)
                except Exception as e:
                    logger.error(f"Error extracting tender from card: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error crawling GEM page {page_num}: {e}")

        return tenders

    async def _extract_tender_data(self, card) -> Dict[str, Any]:
        """Extract data from a tender card"""
        try:
            # Extract bid number/tender ID
            tender_id_elem = await card.query_selector(
                ".bid-number, .tender-id, [class*='bid-no'], [class*='tender-no']"
            )
            tender_id = await tender_id_elem.inner_text() if tender_id_elem else ""

            # Extract title
            title_elem = await card.query_selector(
                ".bid-title, .tender-title, h3, h4, .title, [class*='item-title']"
            )
            title = await title_elem.inner_text() if title_elem else ""

            # Extract description/items
            desc_elem = await card.query_selector(
                ".bid-description, .items, .description, [class*='desc'], p"
            )
            description = await desc_elem.inner_text() if desc_elem else ""

            # Extract end date
            end_date_elem = await card.query_selector(
                ".end-date, .closing-date, [class*='end-date'], [class*='deadline']"
            )
            end_date = await end_date_elem.inner_text() if end_date_elem else ""

            # Extract buyer/organization
            buyer_elem = await card.query_selector(
                ".buyer, .organization, [class*='buyer'], [class*='org']"
            )
            buyer = await buyer_elem.inner_text() if buyer_elem else ""

            # Extract value
            value_elem = await card.query_selector(
                ".value, .amount, [class*='value'], [class*='amount']"
            )
            value = await value_elem.inner_text() if value_elem else ""

            # Extract location
            location_elem = await card.query_selector(
                ".location, [class*='location'], [class*='place']"
            )
            location = await location_elem.inner_text() if location_elem else ""

            # Extract document link
            link_elem = await card.query_selector("a[href*='bid'], a[href*='tender']")
            document_link = await link_elem.get_attribute("href") if link_elem else ""

            if document_link and not document_link.startswith("http"):
                document_link = f"https://bidplus.gem.gov.in{document_link}"

            # Skip if no tender ID or title
            if not tender_id and not title:
                return None

            return {
                "tender_id": tender_id or f"GEM-{hash(title) % 1000000}",
                "title": title,
                "description": description,
                "end_date": end_date,
                "buyer": buyer,
                "value": value,
                "location": location,
                "document_link": document_link,
                "source": "gem"
            }

        except Exception as e:
            logger.error(f"Error extracting tender data: {e}")
            return None


# Standalone function for testing
async def test_gem_crawler():
    """Test GEM crawler"""
    crawler = GEMCrawler()
    results = await crawler.run()
    logger.info(f"Crawl results: {results}")


if __name__ == "__main__":
    asyncio.run(test_gem_crawler())
