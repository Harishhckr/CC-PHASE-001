from typing import List

from rapidfuzz import fuzz


def extract_keywords(text: str, keywords: List[str], threshold: int = 80) -> List[str]:
    matched = set()
    lowered = text.lower()
    for keyword in keywords:
        key = keyword.lower()
        if key in lowered:
            matched.add(keyword)
            continue
        if fuzz.partial_ratio(key, lowered) >= threshold:
            matched.add(keyword)
    return sorted(matched)
