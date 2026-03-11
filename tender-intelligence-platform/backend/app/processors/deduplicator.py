from typing import Dict, List

from rapidfuzz import fuzz


def deduplicate(records: List[Dict]) -> List[Dict]:
    unique = []
    seen = set()
    for record in records:
        key = (record.get("tender_id"), record.get("source"))
        if key in seen:
            record["duplicate_group_id"] = f"{key[0]}-{key[1]}"
            continue
        seen.add(key)
        unique.append(record)
    return unique


def fuzzy_group(records: List[Dict], threshold: int = 90) -> List[Dict]:
    grouped = []
    for record in records:
        duplicate_found = False
        for existing in grouped:
            score = fuzz.token_sort_ratio(record.get("title", ""), existing.get("title", ""))
            if score >= threshold:
                record["duplicate_group_id"] = existing.get("duplicate_group_id") or existing.get("tender_id")
                duplicate_found = True
                break
        if not duplicate_found:
            record["duplicate_group_id"] = record.get("tender_id")
            grouped.append(record)
    return grouped
