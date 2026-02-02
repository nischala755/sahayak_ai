"""
============================================
SAHAYAK AI - YouTube Service
============================================

📌 WHAT IS THIS FILE?
Provides YouTube video search using YouTube Data API v3.
Returns real video links for educational content.

🎓 API QUOTA:
- Free tier: 10,000 units/day
- Search: 100 units per request = ~100 searches/day
- Video details: 1 unit per request

🔑 REQUIREMENTS:
- YouTube Data API enabled in Google Cloud Console
- API key set in YOUTUBE_API_KEY env variable
- Same project as Gemini API works!
============================================
"""

from typing import Dict, Optional, List
import os
import aiohttp
from dataclasses import dataclass


@dataclass
class YouTubeVideo:
    """Represents a YouTube video result"""
    video_id: str
    title: str
    channel: str
    description: str
    thumbnail: str
    duration: Optional[str] = None
    
    @property
    def watch_url(self) -> str:
        return f"https://www.youtube.com/watch?v={self.video_id}"
    
    @property
    def embed_url(self) -> str:
        return f"https://www.youtube.com/embed/{self.video_id}"


# Trusted educational channels for Indian curriculum
TRUSTED_CHANNELS = [
    "Khan Academy India",
    "Khan Academy",
    "BYJU'S",
    "Vedantu",
    "Unacademy",
    "NCERT Official",
    "DIKSHA",
    "LearnVern",
    "Physics Wallah",
    "Topper",
    "CBSE",
    "Magnet Brains",
    "ExamFear",
    "Doubtnut",
]


class YouTubeService:
    """Service for YouTube educational video search"""
    
    API_BASE = "https://www.googleapis.com/youtube/v3"
    
    def __init__(self):
        """Initialize YouTube service"""
        from app.core.config import settings
        self.api_key = settings.youtube_api_key or settings.gemini_api_key
        self.enabled = bool(self.api_key)
        
        if not self.enabled:
            print("⚠️ YouTube API key not found. Using search URL fallback.")
    
    def get_search_url(
        self, 
        query: str,
        add_context: bool = True
    ) -> str:
        """
        Get YouTube search URL (fallback when API unavailable).
        Always works, but returns search results rather than direct video.
        """
        if add_context:
            query = f"{query} NCERT CBSE class"
        
        encoded_query = query.replace(" ", "+")
        return f"https://www.youtube.com/results?search_query={encoded_query}"
    
    async def search_videos(
        self,
        query: str,
        subject: Optional[str] = None,
        grade: Optional[str] = None,
        max_results: int = 3,
        prefer_trusted: bool = True
    ) -> List[YouTubeVideo]:
        """
        Search YouTube for educational videos using Data API.
        
        Args:
            query: Search query (e.g., "fractions")
            subject: Subject context (e.g., "mathematics")
            grade: Grade/class level (e.g., "5")
            max_results: Maximum videos to return (1-5)
            prefer_trusted: Prefer trusted educational channels
            
        Returns:
            List of YouTubeVideo objects with real video IDs
        """
        if not self.enabled:
            return []
        
        # Build search query with educational context
        search_terms = [query]
        if subject:
            search_terms.append(subject)
        if grade:
            search_terms.append(f"class {grade}")
        search_terms.extend(["NCERT", "CBSE", "explain", "Hindi English"])
        
        search_query = " ".join(search_terms)
        
        params = {
            "part": "snippet",
            "q": search_query,
            "type": "video",
            "maxResults": min(max_results * 2, 10),  # Get extra to filter
            "relevanceLanguage": "en",
            "regionCode": "IN",
            "safeSearch": "strict",
            "videoEmbeddable": "true",
            "key": self.api_key,
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.API_BASE}/search",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        print(f"YouTube API error {response.status}: {error_text[:200]}")
                        return []
                    
                    data = await response.json()
        except Exception as e:
            print(f"YouTube API request failed: {e}")
            return []
        
        videos = []
        items = data.get("items", [])
        
        for item in items:
            snippet = item.get("snippet", {})
            video_id = item.get("id", {}).get("videoId")
            
            if not video_id:
                continue
            
            channel = snippet.get("channelTitle", "Unknown")
            
            # Prioritize trusted channels if enabled
            is_trusted = any(
                trusted.lower() in channel.lower() 
                for trusted in TRUSTED_CHANNELS
            )
            
            video = YouTubeVideo(
                video_id=video_id,
                title=snippet.get("title", ""),
                channel=channel,
                description=snippet.get("description", "")[:200],
                thumbnail=snippet.get("thumbnails", {}).get("medium", {}).get("url", ""),
            )
            
            if prefer_trusted and is_trusted:
                videos.insert(0, video)  # Add trusted to front
            else:
                videos.append(video)
        
        return videos[:max_results]
    
    async def get_resource_for_context(
        self,
        subject: str,
        grade: str,
        topic: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Get YouTube resources for a given context.
        Uses API if available, falls back to search URL.
        """
        query = topic or f"{subject} basics"
        
        if self.enabled:
            videos = await self.search_videos(query, subject, grade)
            
            if videos:
                return {
                    "available": True,
                    "type": "direct",
                    "videos": [
                        {
                            "title": v.title,
                            "channel": v.channel,
                            "url": v.watch_url,
                            "thumbnail": v.thumbnail,
                            "icon": "🎬"  # Direct video icon
                        }
                        for v in videos
                    ],
                    "search_url": self.get_search_url(f"{query} {subject} class {grade}")
                }
        
        # Fallback to search URL
        search_url = self.get_search_url(f"{query} {subject} class {grade}")
        
        return {
            "available": True,
            "type": "search",
            "videos": [],
            "search_url": search_url,
            "text": f"🔍 YouTube Search: {query} class {grade}",
            "icon": "🔍"
        }
    
    def format_for_playbook(
        self, 
        videos: List[YouTubeVideo],
        fallback_query: str = ""
    ) -> str:
        """
        Format video list for inclusion in playbook markdown.
        """
        if not videos:
            if fallback_query:
                search_url = self.get_search_url(fallback_query)
                return f"🔍 **Search YouTube**: [{fallback_query}]({search_url})"
            return ""
        
        lines = []
        for i, video in enumerate(videos, 1):
            lines.append(
                f"{i}. 🎬 **[{video.title}]({video.watch_url})** "
                f"- {video.channel}"
            )
        
        return "\n".join(lines)


# Singleton instance
youtube_service = YouTubeService()
