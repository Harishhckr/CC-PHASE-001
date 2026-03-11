import re
from datetime import datetime
from typing import Optional

from dateutil import parser

CURRENCY_MULTIPLIERS = {
    "lakh": 100000,
    "crore": 10000000,
}


def clean_text(text: str) -> str:
    cleaned = re.sub(r"<[^>]+>", " ", text)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def parse_date(value: str) -> Optional[datetime]:
    if not value:
        return None
    try:
        return parser.parse(value, dayfirst=True)
    except (ValueError, TypeError):
        return None


def parse_currency(value: str) -> Optional[float]:
    if not value:
        return None
    cleaned = value.replace("₹", "").replace(",", "").strip().lower()
    for unit, multiplier in CURRENCY_MULTIPLIERS.items():
        if unit in cleaned:
            number = float(cleaned.replace(unit, "").strip())
            return number * multiplier
    try:
        return float(cleaned)
    except ValueError:
        return None


def normalize_source(source: str) -> str:
    return source.strip().lower().replace(" ", "")
