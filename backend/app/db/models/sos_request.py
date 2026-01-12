"""
============================================
SAHAYAK AI - SOS Request Model
============================================

📌 WHAT IS THIS FILE?
Defines the SOS Request document - the core of SAHAYAK AI.
This captures when a teacher needs immediate classroom help.

🎓 LEARNING POINT:
An SOS Request captures:
1. The teacher's problem (voice or text)
2. Classroom context (subject, grade, topic)
3. The urgency level
4. Status tracking (pending → processing → resolved)

Flow:
Teacher speaks/types problem → Context extracted → AI generates playbook
============================================
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum

from beanie import Document, Indexed, Link
from pydantic import Field


class SOSStatus(str, Enum):
    """Status of an SOS request through its lifecycle."""
    PENDING = "pending"          # Just submitted
    PROCESSING = "processing"    # AI is generating playbook
    RESOLVED = "resolved"        # Playbook delivered
    FAILED = "failed"            # AI generation failed


class UrgencyLevel(str, Enum):
    """How urgent is the classroom situation."""
    LOW = "low"          # Can wait, minor confusion
    MEDIUM = "medium"    # Students losing attention
    HIGH = "high"        # Complete breakdown, chaos
    CRITICAL = "critical"  # Safety concern


class ClassroomContext(str, Enum):
    """Type of classroom issue."""
    CONCEPT_CONFUSION = "concept_confusion"      # Students don't understand
    BEHAVIOR_MANAGEMENT = "behavior_management"  # Discipline issues
    ENGAGEMENT_DROP = "engagement_drop"          # Students losing interest
    ACTIVITY_STUCK = "activity_stuck"            # Activity not working
    DIFFERENTIATION = "differentiation"          # Mixed ability levels
    RESOURCE_MISSING = "resource_missing"        # Lack of materials
    TIME_MANAGEMENT = "time_management"          # Running out of time
    OTHER = "other"


class SOSRequest(Document):
    """
    SOS Request document - A teacher's call for help.
    
    This is the primary input to the SAHAYAK AI system.
    Teachers submit their classroom problems, and the AI
    generates immediate teaching rescue playbooks.
    """
    
    # Who submitted
    teacher_id: Indexed(str)  # References User._id
    teacher_name: str  # Denormalized for quick display
    
    # The Problem
    raw_input: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="Raw voice transcript or text input"
    )
    input_type: str = "text"  # "voice" or "text"
    input_language: str = "en"  # Language of input
    
    # Extracted Context (filled by Context Engine)
    subject: Optional[str] = None  # e.g., "Mathematics"
    grade: Optional[str] = None    # e.g., "5"
    topic: Optional[str] = None    # e.g., "Fractions"
    context_type: Optional[ClassroomContext] = None
    student_count: Optional[int] = None
    specific_challenge: Optional[str] = None
    
    # Urgency
    urgency: UrgencyLevel = UrgencyLevel.MEDIUM
    
    # Status
    status: SOSStatus = SOSStatus.PENDING
    
    # AI Processing
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    processing_time_ms: Optional[int] = None  # How long AI took
    
    # Response
    playbook_id: Optional[str] = None  # Reference to generated Playbook
    
    # Feedback
    was_helpful: Optional[bool] = None  # Teacher feedback
    feedback_text: Optional[str] = None
    feedback_rating: Optional[int] = None  # 1-5 stars
    
    # Location Context (for analytics)
    school_id: Optional[str] = None
    district: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "sos_requests"
        use_state_management = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "teacher_id": "65abc123def456",
                "teacher_name": "Priya Sharma",
                "raw_input": "Students are not understanding how to add fractions with different denominators. They keep adding numerators and denominators separately.",
                "input_type": "text",
                "subject": "Mathematics",
                "grade": "5",
                "topic": "Fractions",
                "context_type": "concept_confusion",
                "urgency": "medium",
                "status": "pending"
            }
        }
    
    def start_processing(self):
        """Mark request as being processed."""
        self.status = SOSStatus.PROCESSING
        self.processing_started_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def complete_processing(self, playbook_id: str):
        """Mark request as resolved with playbook."""
        self.status = SOSStatus.RESOLVED
        self.playbook_id = playbook_id
        self.processing_completed_at = datetime.utcnow()
        if self.processing_started_at:
            delta = self.processing_completed_at - self.processing_started_at
            self.processing_time_ms = int(delta.total_seconds() * 1000)
        self.updated_at = datetime.utcnow()
    
    def mark_failed(self):
        """Mark request as failed."""
        self.status = SOSStatus.FAILED
        self.updated_at = datetime.utcnow()
