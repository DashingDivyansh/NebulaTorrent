import re
from typing import Iterable, List

from models.torrent import TorrentResult

TRUSTED_INDEXER_SCORES = {
    "yts": 35,
    "nyaa": 30,
    "eztv": 28,
    "thepiratebay": 20,
}


def get_result_key(result: TorrentResult) -> str:
    if result.infoHash:
        return f"hash:{result.infoHash.lower()}"

    if result.magnet:
        match = re.search(r"xt=urn:btih:([a-zA-Z0-9]+)", result.magnet)
        if match:
            return f"hash:{match.group(1).lower()}"

    normalized_title = re.sub(r"[^a-z0-9]+", " ", result.title.lower()).strip()
    return f"title:{normalized_title}:{result.size}"


def score_result(result: TorrentResult, query: str = "") -> float:
    source_score = 0
    for source in result.source.split(","):
        source_score = max(source_score, TRUSTED_INDEXER_SCORES.get(source.strip().lower(), 10))
    peer_score = max(result.seeders, 0) * 10 + max(result.leechers, 0)
    
    base_score = peer_score + source_score
    relevance_multiplier = 1.0
    
    if query:
        query_words = set(re.findall(r'\w+', query.lower()))
        title_words = set(re.findall(r'\w+', result.title.lower()))
        if query_words:
            matched_words = query_words.intersection(title_words)
            relevance_multiplier = len(matched_words) / len(query_words)
            
            if query.lower() in result.title.lower():
                relevance_multiplier += 0.5
                
            if len(matched_words) < len(query_words):
                relevance_multiplier *= 0.1
                
    return base_score * relevance_multiplier


def deduplicate_and_rank(results: Iterable[TorrentResult], query: str = "") -> List[TorrentResult]:
    unique_results: dict[str, TorrentResult] = {}

    for result in results:
        key = get_result_key(result)
        existing = unique_results.get(key)
        if not existing:
            unique_results[key] = result
            continue

        sources = {s.strip() for s in existing.source.split(",") if s.strip()}
        sources.add(result.source)
        existing.source = ", ".join(sorted(sources))

        if score_result(result, query) > score_result(existing, query):
            existing.seeders = result.seeders
            existing.leechers = result.leechers
            existing.age = result.age or existing.age
            existing.category = result.category or existing.category
            existing.magnet = result.magnet or existing.magnet
            existing.infoHash = result.infoHash or existing.infoHash

    ranked = sorted(unique_results.values(), key=lambda r: score_result(r, query), reverse=True)
    if query:
        ranked = [r for r in ranked if score_result(r, query) > 0]
    return ranked
