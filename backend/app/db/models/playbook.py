"""
============================================
SAHAYAK AI - Teaching Playbook Model
============================================

📌 WHAT IS THIS FILE?
Defines the Playbook document - AI-generated teaching rescue actions.
This is the output of the Gemini Pedagogy Engine.

🎓 LEARNING POINT:
A Playbook is a structured set of actions a teacher can take
immediately to address their classroom situation. It includes:
- Immediate actions (do right now)
- Step-by-step recovery plan
- Alternative strategies
- Success indicators
============================================
"""

from datetime import datetime
from typing import Optional, List

from beanie import Document, Indexed
from pydantic import Field, BaseModel


class VideoResource(BaseModel):
    """A YouTube video resource for teaching."""
    title: str
    url: str
    description: Optional[str] = None
    duration: Optional[str] = None  # e.g., "5:30"


class TeachingResource(BaseModel):
    """An external teaching resource."""
    title: str
    url: str
    resource_type: str  # youtube, ncert, diksha, website
    description: Optional[str] = None


class PlaybookAction(BaseModel):
    """
    A single action in the playbook.
    
    Each action is a specific, actionable instruction
    that the teacher can implement immediately.
    """
    step_number: int
    action: str  # What to do
    duration_minutes: Optional[int] = None  # How long it takes
    materials_needed: List[str] = []  # Any materials required
    teacher_dialogue: Optional[str] = None  # What to say
    expected_outcome: Optional[str] = None  # What should happen


class Playbook(Document):
    """
    Teaching Playbook - AI-generated rescue actions.
    
    This is the main output of SAHAYAK AI. When a teacher
    submits an SOS, the AI generates a playbook with
    immediate, actionable teaching strategies.
    """
    
    # Reference to the SOS request
    sos_request_id: Indexed(str)
    
    # Generated Content
    title: str = Field(
        ...,
        description="Brief title summarizing the rescue strategy"
    )
    summary: str = Field(
        ...,
        description="One-paragraph summary of the approach"
    )
    
    # Immediate Actions (do right now)
    immediate_actions: List[str] = Field(
        default=[],
        description="Quick actions to stabilize the situation"
    )
    
    # Step-by-Step Recovery
    recovery_steps: List[PlaybookAction] = Field(
        default=[],
        description="Detailed recovery actions"
    )
    
    # Alternative Strategies
    alternatives: List[str] = Field(
        default=[],
        description="Alternative approaches if main strategy doesn't work"
    )
    
    # Teacher Support
    teacher_script: Optional[str] = None  # What to say word-by-word
    classroom_arrangement: Optional[str] = None  # How to organize space
    
    # Success Indicators
    success_indicators: List[str] = Field(
        default=[],
        description="How to know if the strategy is working"
    )
    
    # YouTube Video Resources
    youtube_videos: List[VideoResource] = Field(
        default=[],
        description="Relevant YouTube videos for the topic"
    )
    
    # Teaching Resources (NCERT, DIKSHA, etc.)
    teaching_resources: List[TeachingResource] = Field(
        default=[],
        description="External teaching resources and references"
    )
    
    # Quick Teaching Tips
    teaching_tips: List[str] = Field(
        default=[],
        description="Quick tips for the teacher"
    )
    
    # NCERT Chapter Reference
    ncert_reference: Optional[str] = None
    
    # Estimated Impact
    estimated_time_minutes: int = Field(
        default=10,
        ge=1,
        le=45,
        description="Estimated time to implement"
    )
    difficulty_level: str = "medium"  # easy, medium, hard
    
    # AI Metadata
    model_used: str = "gemini-pro"
    prompt_tokens: Optional[int] = None
    response_tokens: Optional[int] = None
    confidence_score: Optional[float] = None  # AI's confidence (0-1)
    
    # Language
    language: str = "en"
    
    # User Interaction
    times_viewed: int = 0
    was_implemented: Optional[bool] = None
    effectiveness_rating: Optional[int] = None  # 1-5
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "playbooks"
        use_state_management = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "sos_request_id": "65abc123def456",
                "title": "Fraction Addition Rescue: Visual Model Approach",
                "summary": "Use paper folding and visual fraction strips to demonstrate why denominators must be the same before adding.",
                "immediate_actions": [
                    "Pause current activity",
                    "Ask students to clear their desks except for one sheet of paper",
                    "Take a deep, calming breath yourself"
                ],
                "recovery_steps": [
                    {
                        "step_number": 1,
                        "action": "Have students fold paper in half, then in thirds",
                        "duration_minutes": 3,
                        "teacher_dialogue": "Let's explore fractions with our hands!",
                        "expected_outcome": "Students physically see 1/2 and 1/3"
                    }
                ],
                "success_indicators": [
                    "Students can explain why 1/2 + 1/3 is not 2/5",
                    "At least 70% can solve a similar problem correctly"
                ],
                "estimated_time_minutes": 15,
                "difficulty_level": "easy"
            }
        }
    
    def record_view(self):
        """Record that the playbook was viewed."""
        self.times_viewed += 1
