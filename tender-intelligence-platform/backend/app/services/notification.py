from typing import List

from app.database.models import Tender, User


def build_daily_digest(user: User, tenders: List[Tender]) -> str:
    lines = [f"Hello {user.full_name or user.username},", "\nToday's tender digest:"]
    for tender in tenders:
        lines.append(f"- {tender.title} ({tender.source})")
    return "\n".join(lines)
