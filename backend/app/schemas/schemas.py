"""
============================================
SAHAYAK AI - Pydantic Schemas
============================================

📌 WHAT IS THIS FILE?
Pydantic schemas for API request/response validation.
These are different from database models - they define
the shape of data that comes in and goes out of the API.

🎓 LEARNING POINT:
- Schemas validate and serialize API data
- They're separate from DB models for flexibility
- Input schemas validate what users send
- Output schemas control what we return
============================================
"""

from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr, Field


# ============================================
# User Schemas
# ============================================

class UserCreate(BaseModel):
    """Schema for creating a new user (registration)."""
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=2, max_length=100)
    role: str = "teacher"
    school_id: Optional[str] = None
    school_name: Optional[str] = None
    district: Optional[str] = None
    phone: Optional[str] = None
    subjects: List[str] = []
    grades: List[str] = []
    preferred_language: str = "en"


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user data in responses."""
    id: str
    email: str
    name: str
    role: str
    school_id: Optional[str] = None
    school_name: Optional[str] = None
    district: Optional[str] = None
    subjects: List[str] = []
    grades: List[str] = []
    preferred_language: str = "en"
    is_active: bool = True
    created_at: datetime
    total_sos_requests: int = 0


class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ============================================
# SOS Request Schemas
# ============================================

class SOSCreate(BaseModel):
    """Schema for creating an SOS request."""
    raw_input: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="The teacher's description of the classroom problem"
    )
    input_type: str = Field(
        default="text",
        description="'text' or 'voice'"
    )
    input_language: str = Field(
        default="en",
        description="Language code (en, hi, kn, etc.)"
    )
    
    # Optional pre-filled context
    subject: Optional[str] = None
    grade: Optional[str] = None
    topic: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "raw_input": "Students in my class 5 math class are not understanding how to add fractions with different denominators. They keep adding numerators and denominators separately.",
                "input_type": "text",
                "input_language": "en",
                "subject": "Mathematics",
                "grade": "5"
            }
        }


class SOSResponse(BaseModel):
    """Schema for SOS request response."""
    id: str
    teacher_id: str
    teacher_name: str
    raw_input: str
    input_type: str
    subject: Optional[str] = None
    grade: Optional[str] = None
    topic: Optional[str] = None
    urgency: str
    status: str
    created_at: datetime
    playbook_id: Optional[str] = None
    processing_time_ms: Optional[int] = None


class SOSWithPlaybook(SOSResponse):
    """SOS response that includes the generated playbook."""
    playbook: Optional[Any] = None


# ============================================
# Playbook Schemas
# ============================================

class VideoResourceSchema(BaseModel):
    """Schema for a YouTube video resource."""
    title: str
    url: str
    description: Optional[str] = None
    duration: Optional[str] = None


class TeachingResourceSchema(BaseModel):
    """Schema for a teaching resource."""
    title: str
    url: str = ""
    resource_type: str
    description: Optional[str] = None


class PlaybookActionSchema(BaseModel):
    """Schema for a playbook action step."""
    step_number: int
    action: str
    duration_minutes: Optional[int] = None
    materials_needed: List[str] = []
    teacher_dialogue: Optional[str] = None
    expected_outcome: Optional[str] = None


class PlaybookResponse(BaseModel):
    """Schema for playbook response."""
    id: str
    sos_request_id: str
    title: str
    summary: str
    immediate_actions: List[str]
    recovery_steps: List[PlaybookActionSchema]
    alternatives: List[str]
    success_indicators: List[str]
    # New YouTube and Resources fields
    youtube_videos: List[VideoResourceSchema] = []
    teaching_resources: List[TeachingResourceSchema] = []
    teaching_tips: List[str] = []
    ncert_reference: Optional[str] = None
    # Metadata
    estimated_time_minutes: int
    difficulty_level: str
    language: str
    created_at: datetime


class PlaybookFeedback(BaseModel):
    """Schema for submitting playbook feedback."""
    was_helpful: bool
    effectiveness_rating: int = Field(..., ge=1, le=5)
    feedback_text: Optional[str] = None


# ============================================
# Dashboard Schemas
# ============================================

class TeacherDashboardResponse(BaseModel):
    """Schema for teacher dashboard data."""
    user: UserResponse
    total_sos_requests: int
    total_successful_resolutions: int
    recent_sos: List[SOSResponse]
    top_issues: List[dict]
    subjects_taught: List[str]


class AnalyticsResponse(BaseModel):
    """Schema for CRP/DIET analytics."""
    total_teachers: int
    total_sos_requests: int
    avg_resolution_time_ms: Optional[float]
    issue_distribution: dict
    subject_distribution: dict
    urgency_distribution: dict
    daily_trends: List[dict]


# ============================================
# General Schemas
# ============================================

class Message(BaseModel):
    """Generic message response."""
    message: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    app_name: str
    version: str
    mongodb_connected: bool
    gemini_available: bool
