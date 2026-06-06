"""
News Feed Ranking Pipeline — Candidate generation, ranking, and re-ranking
Uses ML signals to personalize content for each user.
"""

import time
from typing import List, Dict
from dataclasses import dataclass, field


@dataclass
class Post:
    id: str
    author_id: str
    text: str
    post_type: str  # "text", "photo", "video", "link"
    timestamp: float
    likes: int = 0
    comments: int = 0
    shares: int = 0


@dataclass
class UserSignals:
    user_id: str
    friend_interactions: Dict[str, float] = field(default_factory=dict)  # friend_id -> affinity
    content_preferences: Dict[str, float] = field(default_factory=dict)  # type -> preference score
    active_hours: List[int] = field(default_factory=list)  # hours 0-23
    interests: List[str] = field(default_factory=list)


@dataclass
class FeedItem:
    post: Post
    score: float
    reason: str = ""  # why this post was ranked high


class NewsFeedService:
    """Ranks posts for a user's news feed."""

    def get_feed(self, user_id: str, friend_ids: List[str], posts: List[Post], signals: UserSignals) -> List:
        """Generate and rank a personalized news feed."""
        candidates = [p for p in posts if p.author_id in friend_ids or p.author_id == user_id]
        
        scored = []
        for post in candidates:
            score = self._compute_score(post, user_id, signals)
            if score > 0:
                scored.append(FeedItem(post=post, score=score))
        
        # Sort by score (descending) and insert ads
        scored.sort(key=lambda x: x.score, reverse=True)
        
        # Insert ads every 3-4 items
        feed_with_ads = []
        for i, item in enumerate(scored):
            feed_with_ads.append(item)
            if (i + 1) % 3 == 0:
                feed_with_ads.append({"type": "ad", "message": "[Sponsored Content]"})
        
        return feed_with_ads[:20]  # Return top 20 items

    def _compute_score(self, post: Post, user_id: str, signals: UserSignals) -> float:
        """ML ranking: compute engagement score for a post."""
        score = 0.0
        
        # Friend affinity boost
        if post.author_id in signals.friend_interactions:
            score += signals.friend_interactions[post.author_id] * 10
        
        # Content preference boost
        if post.post_type in signals.content_preferences:
            score += signals.content_preferences[post.post_type] * 5
        
        # Engagement signals
        score += (post.likes / 100) * 2
        score += (post.comments / 50) * 1.5
        score += (post.shares / 20) * 3
        
        # Recency boost (newer is better)
        age_hours = (time.time() - post.timestamp) / 3600
        recency = max(0, 1 - (age_hours / 24))  # Decays over 24 hours
        score += recency * 5
        
        return score
