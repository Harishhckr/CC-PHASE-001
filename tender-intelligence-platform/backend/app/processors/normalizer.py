"""
Data normalizer for cleaning and standardizing tender data
"""
import re
from datetime import datetime
from typing import Optional
from bs4 import BeautifulSoup
from loguru import logger


class DataNormalizer:
    """Data normalization utilities"""

    # Date format patterns
    DATE_FORMATS = [
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%d %b %Y",
        "%d %B %Y",
        "%Y-%m-%d",
        "%d-%m-%Y %H:%M",
        "%d/%m/%Y %H:%M",
        "%d-%b-%Y",
        "%d.%m.%Y",
    ]

    # Currency patterns
    CURRENCY_PATTERNS = {
        "lakh": 100000,
        "lac": 100000,
        "lakhs": 100000,
        "crore": 10000000,
        "crores": 10000000,
        "million": 1000000,
        "billion": 1000000000,
        "k": 1000,
        "m": 1000000,
        "b": 1000000000,
    }

    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""

        # Remove HTML tags
        soup = BeautifulSoup(text, "html.parser")
        text = soup.get_text()

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,;:()\-\/₹$€£@&]', '', text)

        # Trim
        text = text.strip()

        return text

    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date from various formats"""
        if not date_str:
            return None

        # Clean the date string
        date_str = self.clean_text(str(date_str))

        # Try each format
        for fmt in self.DATE_FORMATS:
            try:
                return datetime.strptime(date_str, fmt)
            except (ValueError, TypeError):
                continue

        # Try ISO format
        try:
            return datetime.fromisoformat(date_str)
        except (ValueError, TypeError):
            pass

        logger.warning(f"Could not parse date: {date_str}")
        return None

    def parse_currency(self, value_str: str) -> Optional[float]:
        """Parse Indian currency values"""
        if not value_str:
            return None

        # Convert to string and clean
        value_str = str(value_str).lower()

        # Remove currency symbols
        value_str = re.sub(r'[₹$€£,]', '', value_str)

        # Extract number and multiplier
        match = re.search(r'([\d.]+)\s*([a-z]*)', value_str)
        if not match:
            return None

        try:
            number = float(match.group(1))
            multiplier_str = match.group(2).strip()

            # Apply multiplier
            multiplier = self.CURRENCY_PATTERNS.get(multiplier_str, 1)
            return number * multiplier

        except (ValueError, TypeError) as e:
            logger.warning(f"Could not parse currency: {value_str} - {e}")
            return None

    def standardize_source_name(self, source: str) -> str:
        """Standardize source name"""
        source_mapping = {
            "gem": "gem",
            "gembidplus": "gem",
            "bidplus": "gem",
            "cppp": "cppp",
            "eprocure": "cppp",
            "tenderontime": "tenderontime",
            "tender247": "tender247",
            "tenderdetail": "tenderdetail",
            "tendertiger": "tendertiger"
        }

        source_key = source.lower().replace(" ", "").replace("-", "")
        return source_mapping.get(source_key, source.lower())

    def extract_tender_id(self, text: str, source: str) -> str:
        """Extract tender ID based on source patterns"""
        patterns = {
            "gem": r'(?:GEM|BID)[/\-\s]?(\d+)',
            "cppp": r'(?:CPPP|NIT)[/\-\s]?(\d+)',
            "tender247": r'T247[/\-\s]?(\d+)',
            "tenderdetail": r'TD[/\-\s]?(\d+)',
            "tendertiger": r'TID[/\-\s]?(\d+)',
        }

        pattern = patterns.get(source)
        if pattern:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)

        # Fallback: extract any numeric ID
        match = re.search(r'\d{5,}', text)
        return match.group(0) if match else text

    def normalize_location(self, location: str) -> str:
        """Normalize location string"""
        if not location:
            return ""

        location = self.clean_text(location)

        # Standardize state names
        state_mapping = {
            "tn": "Tamil Nadu",
            "tamilnadu": "Tamil Nadu",
            "mh": "Maharashtra",
            "dl": "Delhi",
            "ka": "Karnataka",
            "up": "Uttar Pradesh",
            "wb": "West Bengal",
            "gj": "Gujarat",
        }

        location_lower = location.lower().replace(" ", "")
        for abbr, full_name in state_mapping.items():
            if abbr in location_lower:
                return full_name

        return location

    def truncate_text(self, text: str, max_length: int = 500) -> str:
        """Truncate text to max length"""
        if not text or len(text) <= max_length:
            return text

        return text[:max_length] + "..."
