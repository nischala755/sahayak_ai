"""
============================================
SAHAYAK AI - Redis Cache Service (Semantic Caching)
============================================

📌 WHAT IS THIS FILE?
Provides SEMANTIC caching functionality using Redis to:
1. Store generated playbooks for faster retrieval
2. Reduce Gemini API calls and costs
3. Improve response times from ~10s to ~50ms for similar queries

🎓 KEY FEATURE - SEMANTIC CACHING:
Instead of hashing the exact input, we cache based on EXTRACTED KEYWORDS:
- Subject (Mathematics, Science, English, etc.)
- Grade (1-12)
- Topic (Fractions, Photosynthesis, Verbs, etc.)

This means ALL of these queries will hit the SAME cache:
- "Class 5 students struggling with fractions"
- "class 5 fractions"
- "fractions class 5"
- "My 5th grade students can't understand fractions"

============================================
"""

import json
from typing import Optional, Dict, Any, List
from redis.asyncio import Redis
from redis.exceptions import ConnectionError, TimeoutError

from app.core.config import settings


class RedisCacheService:
    """
    Async Redis caching service with SEMANTIC matching.
    
    Caching Strategy:
    - Key: "playbook:{subject}:{grade}:{topic}:{language}"
    - Uses EXTRACTED keywords, not raw input hash
    - Similar queries hit the same cache entry
    
    Benefits:
    - "Class 5 fractions" and "students struggling with fractions class 5" = SAME CACHE
    - Reduces Gemini API costs dramatically
    - Drops response time from ~10000ms to ~50ms
    """
    
    def __init__(self):
        """Initialize Redis client (lazy connection)."""
        self._client: Optional[Redis] = None
        self._connected = False
        self._enabled = settings.redis_enabled
        self._ttl = settings.redis_cache_ttl
        
        # Track cache statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "errors": 0,
            "semantic_matches": 0,  # Track semantic cache hits
        }
    
    async def connect(self) -> bool:
        """
        Establish connection to Redis server.
        
        Returns:
            bool: True if connected successfully, False otherwise
        """
        if not self._enabled:
            print("⚠️ Redis caching is disabled (REDIS_ENABLED=false)")
            return False
        
        try:
            self._client = Redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            # Test connection
            await self._client.ping()
            self._connected = True
            print(f"✅ Redis connected: {settings.redis_url}")
            print("   Using SEMANTIC caching (keyword-based matching)")
            return True
        except (ConnectionError, TimeoutError, Exception) as e:
            print(f"⚠️ Redis connection failed: {e}")
            print("   Caching will be disabled - all requests go to Gemini AI")
            self._connected = False
            return False
    
    async def disconnect(self):
        """Close Redis connection gracefully."""
        if self._client:
            await self._client.close()
            self._connected = False
            print("🔌 Redis disconnected")
    
    def is_available(self) -> bool:
        """Check if Redis is available for caching."""
        return self._enabled and self._connected
    
    def _normalize_value(self, value: Optional[str]) -> str:
        """Normalize a value for consistent cache keys."""
        if not value:
            return "general"
        return value.lower().strip().replace(" ", "_").replace("-", "_")
    
    def _generate_semantic_key(
        self,
        subject: Optional[str] = None,
        grade: Optional[str] = None,
        topic: Optional[str] = None,
        language: str = "English"
    ) -> str:
        """
        Generate a SEMANTIC cache key based on extracted context.
        
        Key Format: "playbook:{subject}:{grade}:{topic}:{language}"
        
        This is the PRIMARY cache key - exact match on keywords.
        """
        subject_part = self._normalize_value(subject)
        grade_part = self._normalize_value(grade) if grade else "any"
        topic_part = self._normalize_value(topic) if topic else "general"
        lang_part = self._normalize_value(language)
        
        return f"playbook:{subject_part}:{grade_part}:{topic_part}:{lang_part}"
    
    def _generate_fallback_keys(
        self,
        subject: Optional[str] = None,
        grade: Optional[str] = None,
        topic: Optional[str] = None,
        language: str = "English"
    ) -> List[str]:
        """
        Generate fallback cache keys for broader matching.
        
        If exact key doesn't exist, try progressively broader matches:
        1. subject:grade:topic:lang (exact)
        2. subject:any:topic:lang (ignore grade)
        3. subject:grade:general:lang (ignore topic)
        4. subject:any:general:lang (just subject)
        """
        keys = []
        subject_part = self._normalize_value(subject)
        grade_part = self._normalize_value(grade) if grade else "any"
        topic_part = self._normalize_value(topic) if topic else "general"
        lang_part = self._normalize_value(language)
        
        # Add fallback keys in order of specificity
        if topic_part != "general":
            # Try without grade
            keys.append(f"playbook:{subject_part}:any:{topic_part}:{lang_part}")
        
        if grade_part != "any":
            # Try without topic
            keys.append(f"playbook:{subject_part}:{grade_part}:general:{lang_part}")
        
        # Most general: just subject
        if subject_part != "general":
            keys.append(f"playbook:{subject_part}:any:general:{lang_part}")
        
        return keys
    
    async def get_cached_playbook(
        self,
        subject: Optional[str] = None,
        grade: Optional[str] = None,
        topic: Optional[str] = None,
        language: str = "English"
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a cached playbook using SEMANTIC matching.
        
        First tries exact key, then falls back to broader matches.
        
        Args:
            subject: Detected or provided subject
            grade: Detected or provided grade
            topic: Detected topic (e.g., "fractions", "photosynthesis")
            language: Response language
        
        Returns:
            Cached response dict if found, None otherwise
        """
        if not self.is_available():
            return None
        
        # Generate primary key
        primary_key = self._generate_semantic_key(subject, grade, topic, language)
        
        try:
            # Try primary key first
            cached_data = await self._client.get(primary_key)
            
            if cached_data:
                self.stats["hits"] += 1
                print(f"🎯 CACHE HIT (exact): {primary_key}")
                return json.loads(cached_data)
            
            # Try fallback keys
            fallback_keys = self._generate_fallback_keys(subject, grade, topic, language)
            for fallback_key in fallback_keys:
                cached_data = await self._client.get(fallback_key)
                if cached_data:
                    self.stats["hits"] += 1
                    self.stats["semantic_matches"] += 1
                    print(f"🎯 CACHE HIT (semantic): {fallback_key}")
                    print(f"   Original query was for: {primary_key}")
                    return json.loads(cached_data)
            
            # No cache found
            self.stats["misses"] += 1
            print(f"❌ CACHE MISS: {primary_key}")
            return None
                
        except Exception as e:
            self.stats["errors"] += 1
            print(f"⚠️ Cache read error: {e}")
            return None
    
    async def cache_playbook(
        self,
        response: Dict[str, Any],
        subject: Optional[str] = None,
        grade: Optional[str] = None,
        topic: Optional[str] = None,
        language: str = "English"
    ) -> bool:
        """
        Store a playbook response in cache using semantic key.
        
        Args:
            response: The AI-generated response to cache
            subject: Detected or provided subject
            grade: Detected or provided grade
            topic: Detected topic
            language: Response language
        
        Returns:
            bool: True if cached successfully, False otherwise
        """
        if not self.is_available():
            return False
        
        cache_key = self._generate_semantic_key(subject, grade, topic, language)
        
        try:
            # Serialize response to JSON
            json_data = json.dumps(response, default=str)
            
            # Store with TTL
            await self._client.setex(
                name=cache_key,
                time=self._ttl,
                value=json_data
            )
            
            print(f"💾 CACHED: {cache_key} (TTL: {self._ttl}s)")
            
            # Also store with broader keys for better hit rate
            # Store without grade (so "fractions" queries hit regardless of grade)
            if topic and self._normalize_value(topic) != "general":
                broader_key = f"playbook:{self._normalize_value(subject)}:any:{self._normalize_value(topic)}:{self._normalize_value(language)}"
                existing = await self._client.get(broader_key)
                if not existing:
                    await self._client.setex(broader_key, self._ttl, json_data)
                    print(f"💾 CACHED (broader): {broader_key}")
            
            return True
            
        except Exception as e:
            self.stats["errors"] += 1
            print(f"⚠️ Cache write error: {e}")
            return False
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics for monitoring.
        
        Returns:
            Dict with hit/miss/error counts and hit rate
        """
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total * 100) if total > 0 else 0
        
        stats = {
            "cache_enabled": self._enabled,
            "cache_connected": self._connected,
            "cache_hits": self.stats["hits"],
            "cache_misses": self.stats["misses"],
            "cache_semantic_matches": self.stats["semantic_matches"],
            "cache_errors": self.stats["errors"],
            "cache_hit_rate_percent": round(hit_rate, 2),
            "cache_ttl_seconds": self._ttl,
            "cache_strategy": "semantic (keyword-based)",
        }
        
        # Get Redis info if connected
        if self._connected and self._client:
            try:
                info = await self._client.info("keyspace")
                stats["redis_keys"] = info
            except Exception:
                pass
        
        return stats
    
    async def clear_cache(self, pattern: str = "playbook:*") -> int:
        """
        Clear cached playbooks matching a pattern.
        
        Args:
            pattern: Redis key pattern to match (default: all playbooks)
        
        Returns:
            Number of keys deleted
        """
        if not self.is_available():
            return 0
        
        try:
            keys = []
            async for key in self._client.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                deleted = await self._client.delete(*keys)
                print(f"🗑️ Cleared {deleted} cached playbooks")
                return deleted
            return 0
            
        except Exception as e:
            print(f"⚠️ Cache clear error: {e}")
            return 0


# Singleton instance
redis_cache = RedisCacheService()
