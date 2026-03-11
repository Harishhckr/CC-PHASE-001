import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from tenacity import retry, stop_after_attempt, wait_exponential


@dataclass
class CrawlStats:
    total: int = 0
    success: int = 0
    failed: int = 0
    skipped: int = 0
    errors: List[str] = field(default_factory=list)


class BaseCrawler:
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Mozilla/5.0 (X11; Linux x86_64)",
    ]

    def __init__(self, proxy_pool: Optional[List[str]] = None):
        self.session = requests.Session()
        self.session.mount("https://", HTTPAdapter(max_retries=3))
        self.session.headers.update({"User-Agent": random.choice(self.user_agents)})
        self.proxy_pool = proxy_pool or []
        self.stats = CrawlStats()

    def get_proxy(self) -> Optional[str]:
        if not self.proxy_pool:
            return None
        return random.choice(self.proxy_pool)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def fetch(self, url: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        proxy = self.get_proxy()
        proxies = {"http": proxy, "https": proxy} if proxy else None
        response = self.session.get(url, params=params, proxies=proxies, timeout=30)
        response.raise_for_status()
        return response

    def save_records(self, records: List[Dict[str, Any]]):
        self.stats.total += len(records)
        self.stats.success += len(records)

    def crawl(self) -> List[Dict[str, Any]]:
        raise NotImplementedError
