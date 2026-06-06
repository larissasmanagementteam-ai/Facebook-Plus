"""
Search Engine (Unicorn) — Inverted index, TF-IDF ranking, social boost
Powers Facebook's search across users, posts, pages, events.
"""

import re
from typing import Dict, List, Set
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class SearchDocument:
    id: str
    entity_type: str  # "user", "post", "page", "event"
    title: str
    description: str
    creator_id: str
    tags: List[str] = field(default_factory=list)
    relevance_score: float = 0.5


@dataclass
class SearchResult:
    document: SearchDocument
    score: float


class UnicornSearchEngine:
    """Simulates Facebook's Unicorn search engine."""

    def __init__(self):
        self.documents: Dict[str, SearchDocument] = {}  # doc_id -> doc
        self.inverted_index: Dict[str, Set[str]] = defaultdict(set)  # term -> doc_ids
        self.doc_freq: Dict[str, int] = defaultdict(int)  # term -> count of docs containing it

    def add_document(self, doc: SearchDocument):
        """Index a document."""
        self.documents[doc.id] = doc
        
        # Tokenize and index
        terms = self._tokenize(doc.title + " " + doc.description + " " + " ".join(doc.tags))
        for term in terms:
            self.inverted_index[term].add(doc.id)
            self.doc_freq[term] += 1

    def search(self, query: str, user_id: str, friend_ids: List[str] = None) -> List[SearchResult]:
        """Search for documents (with social ranking boost)."""
        if not friend_ids:
            friend_ids = []
        
        query_terms = self._tokenize(query)
        if not query_terms:
            return []
        
        # Find all docs matching query terms
        matching_docs = set()
        for term in query_terms:
            matching_docs.update(self.inverted_index.get(term, set()))
        
        results = []
        for doc_id in matching_docs:
            doc = self.documents[doc_id]
            score = self._compute_score(doc, query_terms, friend_ids)
            results.append(SearchResult(document=doc, score=score))
        
        # Sort by score (descending)
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:20]  # Top 20 results

    def typeahead(self, prefix: str, user_id: str, friend_ids: List[str] = None) -> List[str]:
        """Autocomplete suggestions based on prefix."""
        if not friend_ids:
            friend_ids = []
        
        suggestions = []
        prefix_lower = prefix.lower()
        
        for doc in self.documents.values():
            if doc.title.lower().startswith(prefix_lower):
                # Boost if creator is a friend
                boost = 1.5 if doc.creator_id in friend_ids else 1.0
                suggestions.append((doc.title, boost * doc.relevance_score))
        
        # Sort by score and return top 10
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in suggestions[:10]]

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into searchable terms."""
        text = text.lower()
        # Remove special chars, split on whitespace
        tokens = re.findall(r'\w+', text)
        return tokens

    def _compute_score(self, doc: SearchDocument, query_terms: List[str], friend_ids: List[str]) -> float:
        """Compute relevance score (TF-IDF with social boost)."""
        score = doc.relevance_score
        
        # TF-IDF approximation
        for term in query_terms:
            if term in self.doc_freq:
                # Term frequency boost (how many query terms match)
                score += 10 / (1 + self.doc_freq[term])
        
        # Social boost: documents from friends rank higher
        if doc.creator_id in friend_ids:
            score *= 1.5
        
        # Type boost
        if doc.entity_type == "user":
            score *= 1.2
        
        return score
