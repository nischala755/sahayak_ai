"""
============================================
SAHAYAK AI - Context Extraction Engine
============================================

📌 WHAT IS THIS FILE?
Extracts structured classroom context from teacher's
raw voice/text input. Uses pattern matching and AI.

🎓 LEARNING POINTS:
This is NLP (Natural Language Processing) in practice:
1. Extract entities: subject, grade, topic
2. Detect sentiment/urgency
3. Classify the issue type
============================================
"""

import re
from typing import Dict, Optional, Any
from app.db.models.sos_request import ClassroomContext, UrgencyLevel


class ContextEngine:
    """
    Extracts classroom context from teacher input.
    
    This processes raw text to identify:
    - Subject being taught
    - Grade/class level
    - Specific topic
    - Type of issue
    - Urgency level
    """
    
    # Subject keywords mapping
    SUBJECT_PATTERNS = {
        "mathematics": ["math", "maths", "mathematics", "गणित", "ಗಣಿತ", "calculation", "numbers", "algebra", "geometry", "fraction", "decimal"],
        "science": ["science", "विज्ञान", "ವಿಜ್ಞಾನ", "physics", "chemistry", "biology", "experiment"],
        "english": ["english", "अंग्रेजी", "ಇಂಗ್ಲಿಷ್", "grammar", "reading", "writing", "comprehension"],
        "hindi": ["hindi", "हिंदी", "ಹಿಂದಿ"],
        "kannada": ["kannada", "ಕನ್ನಡ"],
        "social_studies": ["social", "history", "geography", "civics", "इतिहास", "भूगोल"],
        "evs": ["evs", "environment", "पर्यावरण", "ಪರಿಸರ"],
    }
    
    # Grade patterns
    GRADE_PATTERNS = {
        "1": ["class 1", "grade 1", "first class", "कक्षा 1", "1st grade"],
        "2": ["class 2", "grade 2", "second class", "कक्षा 2", "2nd grade"],
        "3": ["class 3", "grade 3", "third class", "कक्षा 3", "3rd grade"],
        "4": ["class 4", "grade 4", "fourth class", "कक्षा 4", "4th grade"],
        "5": ["class 5", "grade 5", "fifth class", "कक्षा 5", "5th grade"],
        "6": ["class 6", "grade 6", "sixth class", "कक्षा 6", "6th grade"],
        "7": ["class 7", "grade 7", "seventh class", "कक्षा 7", "7th grade"],
        "8": ["class 8", "grade 8", "eighth class", "कक्षा 8", "8th grade"],
        "9": ["class 9", "grade 9", "ninth class", "कक्षा 9", "9th grade"],
        "10": ["class 10", "grade 10", "tenth class", "कक्षा 10", "10th grade"],
    }
    
    # Issue type patterns
    ISSUE_PATTERNS = {
        ClassroomContext.CONCEPT_CONFUSION: [
            "not understanding", "don't understand", "confused",
            "struggling", "difficulty", "can't grasp", "समझ नहीं आ रहा",
            "hard to explain", "wrong answers"
        ],
        ClassroomContext.BEHAVIOR_MANAGEMENT: [
            "misbehaving", "discipline", "noisy", "not listening",
            "fighting", "disrupting", "शोर", "attention problem",
            "out of control", "chaos"
        ],
        ClassroomContext.ENGAGEMENT_DROP: [
            "bored", "not interested", "sleepy", "distracted",
            "lost interest", "not paying attention", "ऊब गए"
        ],
        ClassroomContext.ACTIVITY_STUCK: [
            "activity not working", "stuck", "can't continue",
            "failed activity", "didn't work"
        ],
        ClassroomContext.DIFFERENTIATION: [
            "different levels", "mixed ability", "some understand some don't",
            "fast learners", "slow learners", "gap"
        ],
        ClassroomContext.RESOURCE_MISSING: [
            "no materials", "no textbook", "missing resources",
            "don't have", "need supplies"
        ],
        ClassroomContext.TIME_MANAGEMENT: [
            "running out of time", "no time left", "behind schedule",
            "too slow", "taking too long", "समय कम है"
        ],
    }
    
    # Urgency indicators
    URGENCY_PATTERNS = {
        UrgencyLevel.CRITICAL: [
            "emergency", "urgent", "help now", "immediately",
            "crisis", "safety", "dangerous"
        ],
        UrgencyLevel.HIGH: [
            "very", "really", "completely", "totally",
            "chaos", "out of control", "frustrated"
        ],
        UrgencyLevel.MEDIUM: [
            "having trouble", "some difficulty", "struggling a bit"
        ],
        UrgencyLevel.LOW: [
            "minor", "small", "just wondering", "general question"
        ],
    }
    
    def extract_context(self, raw_input: str) -> Dict[str, Any]:
        """
        Extract classroom context from teacher's input.
        
        Args:
            raw_input: Raw text from teacher (voice transcript or typed)
        
        Returns:
            Dict with extracted context fields
        """
        text = raw_input.lower()
        
        context = {
            "subject": self._extract_subject(text),
            "grade": self._extract_grade(text),
            "topic": self._extract_topic(text),
            "context_type": self._classify_issue(text),
            "urgency": self._detect_urgency(text),
            "student_count": self._extract_student_count(text),
            "specific_challenge": self._extract_specific_challenge(raw_input),
        }
        
        return context
    
    def _extract_subject(self, text: str) -> Optional[str]:
        """Extract the subject being taught."""
        for subject, patterns in self.SUBJECT_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in text:
                    return subject.title()
        return None
    
    def _extract_grade(self, text: str) -> Optional[str]:
        """Extract the grade/class level."""
        for grade, patterns in self.GRADE_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in text:
                    return grade
        
        # Also try regex for patterns like "class 5" or "5th class"
        match = re.search(r'class\s*(\d+)|(\d+)\s*(?:st|nd|rd|th)?\s*(?:class|grade)', text)
        if match:
            return match.group(1) or match.group(2)
        
        return None
    
    def _extract_topic(self, text: str) -> Optional[str]:
        """Extract the specific topic being taught."""
        # Common math topics
        math_topics = [
            "fractions", "decimals", "algebra", "geometry", "multiplication",
            "division", "addition", "subtraction", "percentages", "ratios",
            "shapes", "area", "perimeter", "volume"
        ]
        
        # Common science topics
        science_topics = [
            "plants", "animals", "human body", "matter", "energy",
            "force", "motion", "electricity", "water cycle", "solar system"
        ]
        
        all_topics = math_topics + science_topics
        
        for topic in all_topics:
            if topic in text:
                return topic.title()
        
        return None
    
    def _classify_issue(self, text: str) -> Optional[ClassroomContext]:
        """Classify the type of classroom issue."""
        best_match = None
        best_score = 0
        
        for issue_type, patterns in self.ISSUE_PATTERNS.items():
            score = sum(1 for p in patterns if p.lower() in text)
            if score > best_score:
                best_score = score
                best_match = issue_type
        
        return best_match if best_score > 0 else ClassroomContext.OTHER
    
    def _detect_urgency(self, text: str) -> UrgencyLevel:
        """Detect the urgency level of the request."""
        for level, patterns in self.URGENCY_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in text:
                    return level
        
        return UrgencyLevel.MEDIUM
    
    def _extract_student_count(self, text: str) -> Optional[int]:
        """Extract the number of students if mentioned."""
        patterns = [
            r'(\d+)\s*students',
            r'(\d+)\s*kids',
            r'(\d+)\s*children',
            r'class of\s*(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        
        return None
    
    def _extract_specific_challenge(self, text: str) -> str:
        """Extract or summarize the specific challenge."""
        # For now, just return a cleaned version of the input
        # In a more advanced version, this could use AI summarization
        
        # Remove extra whitespace
        cleaned = " ".join(text.split())
        
        # Truncate if too long
        if len(cleaned) > 200:
            cleaned = cleaned[:200] + "..."
        
        return cleaned


# Singleton instance
context_engine = ContextEngine()
