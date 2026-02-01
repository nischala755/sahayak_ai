"""
============================================
SAHAYAK AI - NCERT Textbook Service
============================================

📌 WHAT IS THIS FILE?
Provides accurate NCERT textbook URLs for Indian school curriculum.
Maps subject/grade/chapter to direct PDF download links.

🎓 NCERT URL PATTERN:
- Textbook page: https://ncert.nic.in/textbook.php?{book_code}={chapter}
- PDF direct: https://ncert.nic.in/textbook/pdf/{book_code}{chapter}.pdf
============================================
"""

from typing import Dict, Optional, List
from dataclasses import dataclass


@dataclass
class NCERTBook:
    """Represents an NCERT textbook"""
    code: str           # Book code used in NCERT URLs
    name: str           # Full book name
    chapters: int       # Total number of chapters
    language: str = "english"  # english, hindi, urdu


# NCERT Book Codes - Based on official NCERT website
# Pattern: First letter = class (a=1, b=2, ..., l=12), Second = language (e=english, h=hindi, u=urdu)
# Third+Fourth = subject code (mh=math, sc=science, ss=social, en=english, hn=hindi)

NCERT_BOOKS: Dict[str, Dict[str, NCERTBook]] = {
    "mathematics": {
        "1": NCERTBook("aemh1", "Math-Magic Book 1", 13),
        "2": NCERTBook("bemh1", "Math-Magic Book 2", 15),
        "3": NCERTBook("cemh1", "Math-Magic Book 3", 14),
        "4": NCERTBook("demh1", "Math-Magic Book 4", 14),
        "5": NCERTBook("eemh1", "Math-Magic Book 5", 14),
        "6": NCERTBook("femh1", "Mathematics Class 6", 14),
        "7": NCERTBook("gemh1", "Mathematics Class 7", 15),
        "8": NCERTBook("hemh1", "Mathematics Class 8", 16),
        "9": NCERTBook("iemh1", "Mathematics Class 9", 15),
        "10": NCERTBook("jemh1", "Mathematics Class 10", 15),
        "11": NCERTBook("kemh1", "Mathematics Class 11", 16),
        "12": NCERTBook("lemh1", "Mathematics Part I Class 12", 13),
    },
    "science": {
        "6": NCERTBook("fesc1", "Science Class 6", 16),
        "7": NCERTBook("gesc1", "Science Class 7", 18),
        "8": NCERTBook("hesc1", "Science Class 8", 18),
        "9": NCERTBook("iesc1", "Science Class 9", 15),
        "10": NCERTBook("jesc1", "Science Class 10", 16),
    },
    "physics": {
        "11": NCERTBook("keph1", "Physics Part I Class 11", 8),
        "12": NCERTBook("leph1", "Physics Part I Class 12", 8),
    },
    "chemistry": {
        "11": NCERTBook("kech1", "Chemistry Part I Class 11", 7),
        "12": NCERTBook("lech1", "Chemistry Part I Class 12", 10),
    },
    "biology": {
        "11": NCERTBook("kebo1", "Biology Class 11", 22),
        "12": NCERTBook("lebo1", "Biology Class 12", 16),
    },
    "english": {
        "1": NCERTBook("aeen1", "Marigold Class 1", 10),
        "2": NCERTBook("been1", "Marigold Class 2", 15),
        "3": NCERTBook("ceen1", "Marigold Class 3", 10),
        "4": NCERTBook("deen1", "Marigold Class 4", 10),
        "5": NCERTBook("eeen1", "Marigold Class 5", 10),
        "6": NCERTBook("fehl1", "Honeysuckle Class 6", 10),
        "7": NCERTBook("gehc1", "Honeycomb Class 7", 10),
        "8": NCERTBook("hehd1", "Honeydew Class 8", 10),
        "9": NCERTBook("iebe1", "Beehive Class 9", 11),
        "10": NCERTBook("jeff1", "First Flight Class 10", 11),
    },
    "hindi": {
        "1": NCERTBook("ahhn1", "Rimjhim Class 1", 23),
        "2": NCERTBook("bhhn1", "Rimjhim Class 2", 15),
        "3": NCERTBook("chhn1", "Rimjhim Class 3", 14),
        "4": NCERTBook("dhhn1", "Rimjhim Class 4", 14),
        "5": NCERTBook("ehhn1", "Rimjhim Class 5", 18),
        "6": NCERTBook("fhvs1", "Vasant Class 6", 17),
        "7": NCERTBook("ghvs1", "Vasant Class 7", 20),
        "8": NCERTBook("hhvs1", "Vasant Class 8", 18),
        "9": NCERTBook("ihks1", "Kshitij Class 9", 17),
        "10": NCERTBook("jhks1", "Kshitij Class 10", 17),
    },
    "social_science": {
        "6": NCERTBook("fess1", "History - Our Pasts I", 12),
        "7": NCERTBook("gess1", "History - Our Pasts II", 10),
        "8": NCERTBook("hess1", "History - Our Pasts III", 12),
        "9": NCERTBook("iess1", "History - India and Contemporary World I", 8),
        "10": NCERTBook("jess3", "History - India and Contemporary World II", 8),
    }
}

# Topic to chapter mapping for common topics
TOPIC_CHAPTER_MAP: Dict[str, Dict[str, Dict[str, int]]] = {
    "fractions": {
        "mathematics": {"5": 4, "6": 7, "7": 2}
    },
    "decimals": {
        "mathematics": {"5": 10, "6": 8, "7": 2}
    },
    "algebra": {
        "mathematics": {"6": 11, "7": 12, "8": 9}
    },
    "geometry": {
        "mathematics": {"6": 4, "7": 6, "8": 3}
    },
    "photosynthesis": {
        "science": {"7": 1, "10": 6}
    },
    "cells": {
        "science": {"8": 8, "9": 5}
    },
    "motion": {
        "science": {"9": 8},
        "physics": {"11": 3}
    },
    "force": {
        "science": {"8": 11, "9": 9}
    },
    "electricity": {
        "science": {"10": 12},
        "physics": {"12": 1}
    },
    "chemical_reactions": {
        "science": {"10": 1},
        "chemistry": {"11": 1}
    }
}


class NCERTService:
    """Service for NCERT textbook references"""
    
    BASE_URL = "https://ncert.nic.in"
    
    def get_textbook_url(
        self, 
        subject: str, 
        grade: str, 
        chapter: Optional[int] = None
    ) -> Optional[Dict[str, str]]:
        """
        Get NCERT textbook URL for a subject/grade/chapter.
        
        Returns dict with:
        - book_name: Full name of the textbook
        - textbook_url: URL to the textbook page
        - pdf_url: Direct PDF download URL (if chapter specified)
        - chapter_list_url: URL to see all chapters
        """
        subject_lower = subject.lower().replace(" ", "_")
        grade_str = str(grade).strip()
        
        # Handle grade variations (5th, class 5, grade 5 -> 5)
        for prefix in ["class", "grade", "th", "st", "nd", "rd"]:
            grade_str = grade_str.replace(prefix, "").strip()
        
        if subject_lower not in NCERT_BOOKS:
            # Try common aliases
            aliases = {
                "maths": "mathematics",
                "math": "mathematics",
                "ganit": "mathematics",
                "physics": "physics",
                "bhautiki": "physics",
                "chemistry": "chemistry",
                "rasayan": "chemistry",
                "bio": "biology",
                "jeev": "biology",
                "social": "social_science",
                "sst": "social_science",
                "history": "social_science",
                "geography": "social_science",
                "civics": "social_science",
            }
            subject_lower = aliases.get(subject_lower, subject_lower)
        
        if subject_lower not in NCERT_BOOKS:
            return None
        
        if grade_str not in NCERT_BOOKS[subject_lower]:
            return None
        
        book = NCERT_BOOKS[subject_lower][grade_str]
        
        result = {
            "book_name": book.name,
            "book_code": book.code,
            "total_chapters": book.chapters,
            "chapter_list_url": f"{self.BASE_URL}/textbook.php?{book.code}=0",
        }
        
        if chapter and 1 <= chapter <= book.chapters:
            # Format chapter number (1 -> 01 for codes, but check actual pattern)
            ch_str = str(chapter)
            result["chapter"] = chapter
            result["textbook_url"] = f"{self.BASE_URL}/textbook.php?{book.code}={chapter}"
            result["pdf_url"] = f"{self.BASE_URL}/textbook/pdf/{book.code}{ch_str.zfill(2)}.pdf"
        
        return result
    
    def get_chapter_for_topic(
        self, 
        topic: str, 
        subject: str, 
        grade: str
    ) -> Optional[int]:
        """
        Try to find the chapter number for a given topic.
        Uses the topic-chapter mapping.
        """
        topic_lower = topic.lower().replace(" ", "_")
        subject_lower = subject.lower().replace(" ", "_")
        grade_str = str(grade).strip()
        
        # Direct lookup
        if topic_lower in TOPIC_CHAPTER_MAP:
            topic_map = TOPIC_CHAPTER_MAP[topic_lower]
            if subject_lower in topic_map:
                return topic_map[subject_lower].get(grade_str)
        
        # Partial matching
        for mapped_topic, subjects in TOPIC_CHAPTER_MAP.items():
            if mapped_topic in topic_lower or topic_lower in mapped_topic:
                if subject_lower in subjects:
                    return subjects[subject_lower].get(grade_str)
        
        return None
    
    def get_resource_for_context(
        self, 
        subject: str, 
        grade: str, 
        topic: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Get the best NCERT resource for a given context.
        Returns formatted resource info.
        """
        chapter = None
        if topic:
            chapter = self.get_chapter_for_topic(topic, subject, grade)
        
        result = self.get_textbook_url(subject, grade, chapter)
        
        if not result:
            return {
                "available": False,
                "message": f"NCERT textbook not found for {subject} class {grade}"
            }
        
        return {
            "available": True,
            "book_name": result["book_name"],
            "chapter": result.get("chapter"),
            "textbook_url": result.get("textbook_url") or result["chapter_list_url"],
            "pdf_url": result.get("pdf_url"),
            "download_text": f"📚 Download NCERT {result['book_name']}" + 
                            (f" Chapter {result['chapter']}" if result.get("chapter") else "")
        }


# Singleton instance
ncert_service = NCERTService()
