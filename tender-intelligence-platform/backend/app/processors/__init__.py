"""
Data processors package
"""
from app.processors.normalizer import DataNormalizer
from app.processors.keyword_filter import KeywordFilter
from app.processors.relevance_scorer import RelevanceScorer
from app.processors.deduplicator import Deduplicator

__all__ = [
    "DataNormalizer",
    "KeywordFilter",
    "RelevanceScorer",
    "Deduplicator",
]
