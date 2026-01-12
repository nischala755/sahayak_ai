"""
============================================
SAHAYAK AI - Classroom Memory Model
============================================

📌 WHAT IS THIS FILE?
Defines the Classroom Memory document - tracks patterns
across a teacher's classroom situations over time.

🎓 LEARNING POINT:
Memory helps SAHAYAK AI:
1. Learn from past issues (pattern detection)
2. Personalize recommendations
3. Track which strategies worked
4. Identify recurring problems for CRP attention
============================================
"""

from datetime import datetime
from typing import Optional, List, Dict

from beanie import Document, Indexed
from pydantic import Field, BaseModel


class IssuePattern(BaseModel):
    """A recurring pattern in classroom issues."""
    issue_type: str  # e.g., "concept_confusion"
    subject: Optional[str] = None
    topic: Optional[str] = None
    occurrence_count: int = 1
    last_occurred: datetime = Field(default_factory=datetime.utcnow)
    
    def increment(self):
        self.occurrence_count += 1
        self.last_occurred = datetime.utcnow()


class SuccessfulStrategy(BaseModel):
    """A strategy that worked well."""
    playbook_id: str
    strategy_summary: str
    subject: Optional[str] = None
    topic: Optional[str] = None
    effectiveness_rating: int  # 1-5
    used_count: int = 1
    last_used: datetime = Field(default_factory=datetime.utcnow)


class ClassroomMemory(Document):
    """
    Classroom Memory - Learning from past situations.
    
    This document aggregates a teacher's classroom
    history to enable smarter, personalized recommendations.
    """
    
    # Owner
    teacher_id: Indexed(str, unique=True)
    
    # Statistics
    total_sos_requests: int = 0
    total_playbooks_generated: int = 0
    total_successful_resolutions: int = 0
    
    # Pattern Tracking
    issue_patterns: List[IssuePattern] = Field(
        default=[],
        description="Recurring issues detected"
    )
    
    # What Works
    successful_strategies: List[SuccessfulStrategy] = Field(
        default=[],
        description="Strategies that worked well"
    )
    
    # Subject-wise Analytics
    subjects_taught: List[str] = []
    subject_issue_count: Dict[str, int] = {}  # {"Math": 5, "Science": 3}
    
    # Time Patterns
    peak_hours: Dict[str, int] = {}  # {"10:00": 5, "14:00": 3}
    day_distribution: Dict[str, int] = {}  # {"Monday": 10, "Tuesday": 8}
    
    # Improvement Tracking
    average_resolution_time_ms: Optional[float] = None
    avg_playbook_rating: Optional[float] = None
    improvement_trend: str = "stable"  # improving, stable, declining
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "classroom_memories"
        use_state_management = True
    
    def record_sos(self, subject: Optional[str] = None, issue_type: Optional[str] = None):
        """Record a new SOS request."""
        self.total_sos_requests += 1
        
        # Update subject stats
        if subject:
            if subject not in self.subjects_taught:
                self.subjects_taught.append(subject)
            self.subject_issue_count[subject] = self.subject_issue_count.get(subject, 0) + 1
        
        # Update patterns
        if issue_type:
            found = False
            for pattern in self.issue_patterns:
                if pattern.issue_type == issue_type and pattern.subject == subject:
                    pattern.increment()
                    found = True
                    break
            if not found:
                self.issue_patterns.append(
                    IssuePattern(issue_type=issue_type, subject=subject)
                )
        
        self.updated_at = datetime.utcnow()
    
    def record_successful_strategy(
        self,
        playbook_id: str,
        summary: str,
        rating: int,
        subject: Optional[str] = None,
        topic: Optional[str] = None
    ):
        """Record a strategy that worked."""
        self.total_successful_resolutions += 1
        
        # Check if we already have this strategy
        for strategy in self.successful_strategies:
            if strategy.playbook_id == playbook_id:
                strategy.used_count += 1
                strategy.last_used = datetime.utcnow()
                return
        
        # Add new strategy
        self.successful_strategies.append(
            SuccessfulStrategy(
                playbook_id=playbook_id,
                strategy_summary=summary,
                subject=subject,
                topic=topic,
                effectiveness_rating=rating
            )
        )
        self.updated_at = datetime.utcnow()
    
    def get_top_issues(self, limit: int = 5) -> List[IssuePattern]:
        """Get the most common issues."""
        sorted_patterns = sorted(
            self.issue_patterns,
            key=lambda x: x.occurrence_count,
            reverse=True
        )
        return sorted_patterns[:limit]
    
    def get_best_strategies(self, limit: int = 5) -> List[SuccessfulStrategy]:
        """Get the most effective strategies."""
        sorted_strategies = sorted(
            self.successful_strategies,
            key=lambda x: (x.effectiveness_rating, x.used_count),
            reverse=True
        )
        return sorted_strategies[:limit]
