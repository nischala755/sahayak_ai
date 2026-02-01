"""
============================================
SAHAYAK AI - DIKSHA Service
============================================

📌 WHAT IS THIS FILE?
Provides DIKSHA (Digital Infrastructure for Knowledge Sharing)
content links and mappings for Indian school curriculum.

🎓 DIKSHA LINKS:
- Web: https://diksha.gov.in/explore-course/...
- App: diksha://play/content/...
- Search: https://diksha.gov.in/search?key=...
============================================
"""

from typing import Dict, Optional, List
from dataclasses import dataclass
import os


@dataclass
class DIKSHAContent:
    """Represents a DIKSHA content item"""
    content_id: str
    title: str
    subject: str
    grade: str
    topic: str
    content_type: str  # "video", "course", "resource"
    language: str = "english"


# Pre-mapped popular DIKSHA content IDs for quick access
# These are real content IDs from DIKSHA platform
DIKSHA_CONTENT_MAP: Dict[str, Dict[str, Dict[str, str]]] = {
    # Format: topic -> subject -> grade -> content_id
    "fractions": {
        "mathematics": {
            "5": "do_31307360985432064011843",
            "6": "do_31307361029767168011914", 
            "7": "do_31310347499001446411662",
        }
    },
    "decimals": {
        "mathematics": {
            "5": "do_31307361058553446411992",
            "6": "do_31310347590830489611835",
        }
    },
    "algebra": {
        "mathematics": {
            "7": "do_31307361170044518412243",
            "8": "do_31310348148426342411907",
        }
    },
    "photosynthesis": {
        "science": {
            "7": "do_31307361251647078412404",
            "10": "do_31310348314580992012187",
        }
    },
    "cells": {
        "science": {
            "8": "do_31307361325785088012565",
            "9": "do_31310348455229849612438",
        }
    },
    "motion": {
        "science": {
            "9": "do_31307361394821324812726",
        }
    },
    "electricity": {
        "science": {
            "10": "do_31307361459507404812887",
        }
    },
    "english_grammar": {
        "english": {
            "5": "do_31307361528193638413048",
            "6": "do_31310348648653209612689",
        }
    },
    "hindi_vyakaran": {
        "hindi": {
            "5": "do_31307361597880115213209",
            "6": "do_31310348798918246412940",
        }
    }
}

# Board-wise search prefixes
BOARD_PREFIXES = {
    "cbse": "",
    "ncert": "",
    "state": "",
}


class DIKSHAService:
    """Service for DIKSHA educational content"""
    
    WEB_BASE = "https://diksha.gov.in"
    APP_SCHEME = "diksha://play"
    
    def __init__(self):
        """Initialize DIKSHA service"""
        # In future, can connect to database for content mappings
        self.use_database = os.getenv("DIKSHA_USE_DATABASE", "false").lower() == "true"
    
    def get_content_url(
        self, 
        content_id: str, 
        link_type: str = "web"
    ) -> str:
        """
        Get DIKSHA content URL for a given content ID.
        
        Args:
            content_id: DIKSHA content ID (e.g., do_31307360985432064011843)
            link_type: "web" for browser, "app" for app deep link
        """
        if link_type == "app":
            return f"{self.APP_SCHEME}/content/{content_id}"
        return f"{self.WEB_BASE}/play/content/{content_id}"
    
    def get_search_url(
        self, 
        query: str, 
        subject: Optional[str] = None,
        grade: Optional[str] = None,
        board: str = "cbse"
    ) -> str:
        """
        Get DIKSHA search URL for a topic.
        
        This always works as a fallback when specific content ID isn't known.
        """
        search_terms = [query]
        if subject:
            search_terms.append(subject)
        if grade:
            search_terms.append(f"class {grade}")
        
        search_query = " ".join(search_terms)
        # URL encode the query
        encoded_query = search_query.replace(" ", "%20")
        
        return f"{self.WEB_BASE}/search/Library/1?key={encoded_query}&selectedTab=all"
    
    def get_content_for_topic(
        self, 
        topic: str, 
        subject: str, 
        grade: str
    ) -> Optional[Dict[str, str]]:
        """
        Try to find a specific DIKSHA content for a topic.
        Uses pre-mapped content IDs.
        """
        topic_lower = topic.lower().replace(" ", "_")
        subject_lower = subject.lower().replace(" ", "_")
        grade_str = str(grade).strip()
        
        # Direct lookup
        if topic_lower in DIKSHA_CONTENT_MAP:
            topic_map = DIKSHA_CONTENT_MAP[topic_lower]
            if subject_lower in topic_map:
                if grade_str in topic_map[subject_lower]:
                    content_id = topic_map[subject_lower][grade_str]
                    return {
                        "content_id": content_id,
                        "web_url": self.get_content_url(content_id, "web"),
                        "app_url": self.get_content_url(content_id, "app"),
                        "type": "direct"
                    }
        
        # Partial matching
        for mapped_topic, subjects in DIKSHA_CONTENT_MAP.items():
            if mapped_topic in topic_lower or topic_lower in mapped_topic:
                if subject_lower in subjects:
                    if grade_str in subjects[subject_lower]:
                        content_id = subjects[subject_lower][grade_str]
                        return {
                            "content_id": content_id,
                            "web_url": self.get_content_url(content_id, "web"),
                            "app_url": self.get_content_url(content_id, "app"),
                            "type": "direct"
                        }
        
        return None
    
    def get_resource_for_context(
        self, 
        subject: str, 
        grade: str, 
        topic: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Get the best DIKSHA resource for a given context.
        Falls back to search URL if specific content not found.
        """
        # Try direct content lookup first
        if topic:
            direct_content = self.get_content_for_topic(topic, subject, grade)
            if direct_content:
                return {
                    "available": True,
                    "type": "direct",
                    "content_id": direct_content["content_id"],
                    "web_url": direct_content["web_url"],
                    "app_url": direct_content["app_url"],
                    "text": f"📱 DIKSHA: Watch lesson on {topic}",
                    "search_url": None
                }
        
        # Fallback to search URL
        search_query = topic or subject
        search_url = self.get_search_url(search_query, subject, grade)
        
        return {
            "available": True,
            "type": "search",
            "content_id": None,
            "web_url": search_url,
            "app_url": f"diksha://search?key={search_query}",
            "text": f"🔍 DIKSHA: Search {search_query} resources",
            "search_url": search_url
        }
    
    def get_all_resources(
        self,
        subject: str,
        grade: str,
        topic: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Get all DIKSHA resources (both direct and search).
        """
        resources = []
        
        # Direct content
        if topic:
            direct = self.get_content_for_topic(topic, subject, grade)
            if direct:
                resources.append({
                    "type": "direct",
                    "title": f"DIKSHA Lesson: {topic}",
                    "web_url": direct["web_url"],
                    "app_url": direct["app_url"],
                    "icon": "📱"
                })
        
        # Search link (always include as fallback)
        search_url = self.get_search_url(topic or subject, subject, grade)
        resources.append({
            "type": "search", 
            "title": f"Search DIKSHA for more {topic or subject} content",
            "web_url": search_url,
            "app_url": f"diksha://search?key={topic or subject}",
            "icon": "🔍"
        })
        
        return resources


# Singleton instance
diksha_service = DIKSHAService()
