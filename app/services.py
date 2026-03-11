from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable
from zipfile import ZipFile

from xml.etree import ElementTree


@dataclass(frozen=True)
class MDMResult:
    score: float
    matched_keywords: list[str]


def normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def calculate_relevance(text: str, keywords: Iterable[str]) -> MDMResult:
    normalized = normalize_text(text)
    keyword_list = [kw.strip().lower() for kw in keywords if kw.strip()]
    if not keyword_list:
        return MDMResult(score=0.0, matched_keywords=[])

    matched = [kw for kw in keyword_list if kw in normalized]
    score = min(100.0, round((len(matched) / len(keyword_list)) * 100, 2))
    return MDMResult(score=score, matched_keywords=matched)


def parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def load_keywords(path: str) -> list[str]:
    if path.endswith(".docx"):
        return load_keywords_from_docx(path)
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return [line.strip() for line in handle if line.strip()]
    except FileNotFoundError:
        return []


def load_keywords_from_docx(path: str) -> list[str]:
    try:
        with ZipFile(path) as archive:
            xml_data = archive.read("word/document.xml")
    except FileNotFoundError:
        return []
    except KeyError:
        return []

    root = ElementTree.fromstring(xml_data)
    namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    texts = [node.text for node in root.iter(f"{namespace}t") if node.text]
    raw_text = " ".join(texts)
    if not raw_text.strip():
        return []
    keywords = [item.strip() for item in raw_text.replace("\n", " ").split(",")]
    return [kw for kw in keywords if kw]
