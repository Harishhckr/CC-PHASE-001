from datetime import datetime
from typing import Dict, List, Optional


def score_tender(
    matched_keywords: List[str],
    keyword_weights: Dict[str, int],
    published_date: Optional[datetime] = None,
    value: Optional[float] = None,
    preferred_locations: Optional[List[str]] = None,
    location: Optional[str] = None,
) -> float:
    base_score = 0.0
    for keyword in matched_keywords:
        base_score += keyword_weights.get(keyword, 0)
    if matched_keywords:
        base_score += min(15, len(matched_keywords) * 2)

    recency_boost = 0.0
    if published_date:
        days_old = max((datetime.utcnow() - published_date).days, 0)
        recency_boost = max(0, 20 - days_old)

    value_boost = 0.0
    if value:
        if value > 1_000_000:
            value_boost = 15
        elif value > 100_000:
            value_boost = 8
        else:
            value_boost = 3

    location_boost = 0.0
    if preferred_locations and location:
        for preferred in preferred_locations:
            if preferred.lower() in location.lower():
                location_boost = 10
                break

    score = base_score + recency_boost + value_boost + location_boost
    return min(100.0, round(score, 2))
