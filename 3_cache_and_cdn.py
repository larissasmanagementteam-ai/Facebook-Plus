"""
Cache + CDN — Memcached simulation and CDN edge node caching
ImprovesLatency and reduces database load.
"""

import time
from typing import Dict, Tuple, Callable, Optional


class MemcachedSimulator:
    """Simulates Memcached in-memory cache."""

    def __init__(self, ttl: int = 3600):
        self.cache: Dict[str, Tuple[object, float]] = {}  # key -> (value, expiry_time)
        self.ttl = ttl
        self.hits = 0
        self.misses = 0

    def set(self, key: str, value: object, ttl: int = None):
        """Set a value in cache."""
        expiry = time.time() + (ttl or self.ttl)
        self.cache[key] = (value, expiry)

    def get(self, key: str) -> Optional[object]:
        """Get a value from cache."""
        if key in self.cache:
            value, expiry = self.cache[key]
            if time.time() < expiry:
                self.hits += 1
                return value
            else:
                del self.cache[key]
        self.misses += 1
        return None

    def delete(self, key: str):
        """Delete a key from cache."""
        if key in self.cache:
            del self.cache[key]

    def hit_rate(self) -> float:
        """Return cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


class DatabaseSimulator:
    """Simulates a database with read latency."""

    def __init__(self, latency_ms: float = 100):
        self.data: Dict[str, object] = {}
        self.latency_ms = latency_ms

    def read(self, key: str) -> Optional[object]:
        """Read from database (simulates latency)."""
        time.sleep(self.latency_ms / 1000)
        return self.data.get(key)

    def write(self, key: str, value: object):
        """Write to database."""
        self.data[key] = value


class CacheLayer:
    """Look-aside cache pattern: check cache first, then database."""

    def __init__(self, cache: MemcachedSimulator, db: DatabaseSimulator):
        self.cache = cache
        self.db = db

    def get(self, key: str) -> Tuple[object, str]:
        """Get value from cache or database."""
        # Try cache first
        cached = self.cache.get(key)
        if cached is not None:
            return cached, "cache"
        
        # Fall back to database
        db_value = self.db.read(key)
        if db_value is not None:
            self.cache.set(key, db_value)
            return db_value, "database"
        
        return None, "miss"

    def set(self, key: str, value: object):
        """Write to database and cache."""
        self.db.write(key, value)
        self.cache.set(key, value)

    def hit_rate(self) -> float:
        """Return cache hit rate."""
        return self.cache.hit_rate()


class CDNEdgeNode:
    """Simulates a CDN edge node for geographic distribution."""

    def __init__(self, region: str):
        self.region = region
        self.cache: Dict[str, Dict] = {}  # media_id -> {resolution -> blob}

    def fetch(self, media_id: str, resolution: str, origin_fn: Callable = None) -> Dict:
        """Fetch media, checking cache first, then origin."""
        # Check if in edge cache
        if media_id in self.cache and resolution in self.cache[media_id]:
            return {
                "media_id": media_id,
                "resolution": resolution,
                "source": f"CDN-{self.region}",
                "blob": self.cache[media_id][resolution]
            }
        
        # Fetch from origin
        if origin_fn:
            blob = origin_fn(media_id, resolution)
            if media_id not in self.cache:
                self.cache[media_id] = {}
            self.cache[media_id][resolution] = blob
            return {
                "media_id": media_id,
                "resolution": resolution,
                "source": "origin",
                "blob": blob
            }
        
        return None
