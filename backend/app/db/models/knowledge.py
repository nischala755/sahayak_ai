"""
============================================
SAHAYAK AI - Knowledge Exchange Model
============================================
Teacher-to-Teacher Knowledge Sharing System
Classroom Decision Library with trust scores
============================================
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum

from beanie import Document, Indexed
from pydantic import BaseModel, Field


class SolutionStatus(str, Enum):
    """Status of a shared solution."""
    PENDING = "pending"
    APPROVED = "approved"
    FEATURED = "featured"
    ARCHIVED = "archived"


class ValidationVote(BaseModel):
    """A teacher's vote on a solution."""
    teacher_id: str
    teacher_name: str
    vote: int  # 1 = helpful, -1 = not helpful
    comment: Optional[str] = None
    voted_at: datetime = Field(default_factory=datetime.utcnow)


class SharedSolution(Document):
    """
    Teacher-shared classroom solution.
    Part of the Knowledge Exchange / Classroom Decision Library.
    """
    # Source
    teacher_id: Indexed(str)
    teacher_name: str
    school_id: Optional[str] = None
    district: Optional[str] = None
    
    # Problem context
    problem_description: str = Field(..., min_length=10, max_length=2000)
    subject: Optional[str] = None
    grade: Optional[str] = None
    topic: Optional[str] = None
    context_type: Optional[str] = None  # concept_confusion, discipline, etc.
    
    # Solution
    solution_title: str = Field(..., min_length=5, max_length=200)
    solution_description: str = Field(..., min_length=20, max_length=5000)
    steps: List[str] = []  # Step-by-step approach
    materials_needed: List[str] = []
    time_required_minutes: Optional[int] = None
    
    # AI Enhancement
    original_playbook_id: Optional[str] = None  # If derived from AI playbook
    ai_enhanced: bool = False  # If AI helped refine it
    
    # Anonymization
    is_anonymous: bool = True  # Show as "A Teacher from [District]"
    
    # Trust & Validation
    trust_score: float = Field(default=0.0, ge=0.0, le=5.0)
    usage_count: int = 0
    validation_votes: List[ValidationVote] = []
    helpful_count: int = 0
    not_helpful_count: int = 0
    
    # Status
    status: SolutionStatus = SolutionStatus.PENDING
    
    # Metadata
    tags: List[str] = []
    language: str = "en"
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "shared_solutions"
        use_state_management = True
    
    def add_vote(self, teacher_id: str, teacher_name: str, vote: int, comment: str = None):
        """Add or update a validation vote."""
        # Remove existing vote from this teacher
        self.validation_votes = [v for v in self.validation_votes if v.teacher_id != teacher_id]
        
        # Add new vote
        self.validation_votes.append(ValidationVote(
            teacher_id=teacher_id,
            teacher_name=teacher_name,
            vote=vote,
            comment=comment
        ))
        
        # Recalculate counts
        self.helpful_count = sum(1 for v in self.validation_votes if v.vote > 0)
        self.not_helpful_count = sum(1 for v in self.validation_votes if v.vote < 0)
        
        # Update trust score (Wilson score interval approximation)
        total = self.helpful_count + self.not_helpful_count
        if total > 0:
            positive_ratio = self.helpful_count / total
            # Simple weighted score with usage
            self.trust_score = min(5.0, (positive_ratio * 4) + (min(self.usage_count, 100) / 100))
        
        self.updated_at = datetime.utcnow()
    
    def increment_usage(self):
        """Track when solution is viewed/used."""
        self.usage_count += 1
        self.updated_at = datetime.utcnow()


class NCERTReference(Document):
    """
    NCERT Chapter and Topic Mapping.
    Used for grounding AI responses with curriculum references.
    """
    # Book identification
    class_level: Indexed(str)  # "5", "6", etc.
    subject: Indexed(str)
    book_name: str
    
    # Chapter info
    chapter_number: int
    chapter_name: str
    
    # Topics covered
    topics: List[str] = []
    keywords: List[str] = []  # For search matching
    
    # Page references
    start_page: Optional[int] = None
    end_page: Optional[int] = None
    
    # Learning objectives
    learning_objectives: List[str] = []
    
    # FLN mapping (Foundational Literacy and Numeracy)
    fln_competencies: List[str] = []
    
    # Metadata
    language: str = "en"
    state_board: str = "NCERT"  # Can be KSEEB, SCERT, etc.
    
    class Settings:
        name = "ncert_references"
    
    @classmethod
    async def find_by_topic(cls, topic: str, grade: str = None, subject: str = None):
        """Find NCERT references matching a topic."""
        query = {}
        if grade:
            query["class_level"] = grade
        if subject:
            query["subject"] = subject
        
        # Search in topics and keywords
        references = await cls.find(query).to_list()
        
        # Filter by topic match
        topic_lower = topic.lower()
        matched = [
            ref for ref in references
            if any(topic_lower in t.lower() for t in ref.topics) or
               any(topic_lower in k.lower() for k in ref.keywords)
        ]
        
        return matched


class TeacherMentorProfile(Document):
    """
    AI Teaching Mentor - Personalized teacher coaching profile.
    Tracks patterns, suggests interventions, generates insights.
    """
    teacher_id: Indexed(str, unique=True)
    teacher_name: str
    
    # Teaching patterns
    common_subjects: List[str] = []
    common_grades: List[str] = []
    common_issues: List[str] = []  # Types of problems faced
    
    # Strengths & Areas for Growth
    identified_strengths: List[str] = []
    growth_areas: List[str] = []
    
    # Learning progress
    total_sos_requests: int = 0
    resolved_successfully: int = 0
    playbooks_found_helpful: int = 0
    
    # Patterns detected
    peak_sos_hours: List[int] = []  # Hours of day with most SOS
    peak_sos_days: List[int] = []   # Days of week (0=Mon)
    recurring_topics: List[dict] = []  # [{topic, count, last_seen}]
    
    # Mentor suggestions
    pending_nudges: List[dict] = []  # Micro-learning suggestions
    completed_nudges: List[str] = []
    
    # Weekly reports
    last_weekly_report: Optional[dict] = None
    weekly_report_sent_at: Optional[datetime] = None
    
    # Engagement
    last_active: Optional[datetime] = None
    engagement_score: float = 0.0  # 0-100
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "teacher_mentor_profiles"
        use_state_management = True
    
    def update_from_sos(self, sos_request):
        """Update profile based on new SOS request."""
        self.total_sos_requests += 1
        self.last_active = datetime.utcnow()
        
        # Track subjects and grades
        if sos_request.subject and sos_request.subject not in self.common_subjects:
            self.common_subjects.append(sos_request.subject)
        if sos_request.grade and sos_request.grade not in self.common_grades:
            self.common_grades.append(sos_request.grade)
        
        # Track issue types
        if sos_request.context_type:
            issue = sos_request.context_type.value
            if issue not in self.common_issues:
                self.common_issues.append(issue)
        
        # Track time patterns
        hour = sos_request.created_at.hour
        if hour not in self.peak_sos_hours:
            self.peak_sos_hours.append(hour)
        
        day = sos_request.created_at.weekday()
        if day not in self.peak_sos_days:
            self.peak_sos_days.append(day)
        
        self.updated_at = datetime.utcnow()
    
    def generate_insights(self) -> dict:
        """Generate AI mentor insights for this teacher."""
        insights = {
            "patterns": [],
            "suggestions": [],
            "strengths": self.identified_strengths,
            "growth_areas": self.growth_areas,
        }
        
        # Analyze patterns
        if len(self.peak_sos_hours) > 0:
            common_hour = max(set(self.peak_sos_hours), key=self.peak_sos_hours.count)
            if common_hour < 12:
                insights["patterns"].append("Most challenges occur in morning sessions")
            else:
                insights["patterns"].append("Most challenges occur in afternoon sessions")
        
        # Generate suggestions based on common issues
        for issue in self.common_issues[:3]:
            if issue == "concept_confusion":
                insights["suggestions"].append("Try using more visual aids and manipulatives")
            elif issue == "discipline":
                insights["suggestions"].append("Consider implementing classroom management techniques")
            elif issue == "engagement":
                insights["suggestions"].append("Incorporate more interactive activities")
        
        return insights


class OfflinePackVersion(Document):
    """
    Offline Knowledge Pack versioning.
    Tracks what's available for offline use.
    """
    version: str  # e.g., "2.1.0"
    language: str
    grade: Optional[str] = None
    
    # Content
    problem_count: int = 0
    solution_count: int = 0
    
    # File info
    file_size_bytes: int = 0
    file_hash: Optional[str] = None
    
    # Status
    is_active: bool = True
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "offline_pack_versions"
