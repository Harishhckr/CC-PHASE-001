from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

import requests
from bs4 import BeautifulSoup

from .services import parse_date


@dataclass
class TenderPayload:
    tender_id: str
    description: str
    start_date: datetime | None
    end_date: datetime | None
    document_links: list[str]
    source: str


class BaseScraper:
    source: str
    url: str

    def __init__(self, user_agent: str) -> None:
        self.user_agent = user_agent

    def fetch(self) -> str:
        response = requests.get(self.url, headers={"User-Agent": self.user_agent}, timeout=30)
        response.raise_for_status()
        return response.text

    def parse(self, html: str) -> Iterable[TenderPayload]:
        raise NotImplementedError

    def run(self) -> Iterable[TenderPayload]:
        return self.parse(self.fetch())


class CPPPScraper(BaseScraper):
    source = "CPP Portal"
    url = "https://eprocure.gov.in/cppp/tenderslatest?"  # Example endpoint

    def parse(self, html: str) -> Iterable[TenderPayload]:
        soup = BeautifulSoup(html, "html.parser")
        rows = soup.select("table tbody tr")
        for row in rows[:10]:
            columns = [col.get_text(strip=True) for col in row.find_all("td")]
            if len(columns) < 4:
                continue
            tender_id = columns[0]
            description = columns[1]
            start_date = parse_date(columns[2])
            end_date = parse_date(columns[3])
            document_links = [link["href"] for link in row.select("a") if link.get("href")]
            yield TenderPayload(
                tender_id=tender_id,
                description=description,
                start_date=start_date,
                end_date=end_date,
                document_links=document_links,
                source=self.source,
            )


class GeMSScraper(BaseScraper):
    source = "GeM"
    url = "https://gem.gov.in/tenders"  # Example endpoint

    def parse(self, html: str) -> Iterable[TenderPayload]:
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select(".card")
        for card in cards[:10]:
            tender_id = card.get("data-id") or "GEM-UNKNOWN"
            description = card.get_text(" ", strip=True)
            date_nodes = card.select(".tender-date")
            start_date = parse_date(date_nodes[0].get_text(strip=True)) if date_nodes else None
            end_date = parse_date(date_nodes[1].get_text(strip=True)) if len(date_nodes) > 1 else None
            document_links = [link["href"] for link in card.select("a") if link.get("href")]
            yield TenderPayload(
                tender_id=tender_id,
                description=description,
                start_date=start_date,
                end_date=end_date,
                document_links=document_links,
                source=self.source,
            )


class StatePortalScraper(BaseScraper):
    source = "State Portal"
    url = "https://eprocure.tn.gov.in/tenders"  # Example endpoint

    def parse(self, html: str) -> Iterable[TenderPayload]:
        soup = BeautifulSoup(html, "html.parser")
        items = soup.select(".tender-item")
        for item in items[:10]:
            tender_id = item.get("data-tender-id") or "STATE-UNKNOWN"
            description = item.get_text(" ", strip=True)
            start_date = parse_date(item.get("data-start"))
            end_date = parse_date(item.get("data-end"))
            document_links = [link["href"] for link in item.select("a") if link.get("href")]
            yield TenderPayload(
                tender_id=tender_id,
                description=description,
                start_date=start_date,
                end_date=end_date,
                document_links=document_links,
                source=self.source,
            )


def get_scrapers(user_agent: str) -> list[BaseScraper]:
    return [CPPPScraper(user_agent), GeMSScraper(user_agent), StatePortalScraper(user_agent)]
