"""
============================================
SAHAYAK AI - User Model
============================================

📌 WHAT IS THIS FILE?
Defines the User document model for MongoDB.
Users can be Teachers, CRPs (Cluster Resource Persons),
or DIET (District Institute of Education and Training) admins.

🎓 LEARNING POINT:
Beanie documents are Python classes that map to MongoDB documents.
Each field has a type hint, and Beanie handles the conversion.

Example MongoDB document:
{
    "_id": ObjectId("..."),
    "email": "teacher@school.gov.in",
    "name": "Priya Sharma",
    "role": "teacher",
    "school_id": "KA-BGM-001",
    ...
}
============================================
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum

from beanie import Document, Indexed
from pydantic import EmailStr, Field


class UserRole(str, Enum):
    """
    User roles in the SAHAYAK AI system.
    
    - teacher: Classroom teachers who use SOS feature
    - crp: Cluster Resource Persons who mentor teachers
    - diet: District-level administrators with analytics access
    """
    TEACHER = "teacher"
    CRP = "crp"
    DIET = "diet"


class User(Document):
    """
    User document model for SAHAYAK AI.
    
    This represents teachers and education administrators
    who use the classroom coaching system.
    
    🎓 LEARNING POINT:
    - Indexed() creates a MongoDB index for faster queries
    - Field() adds validation and metadata
    - Optional[] means the field can be None
    """
    
    # Basic Info
    email: Indexed(EmailStr, unique=True)  # Indexed for fast lookup
    name: str = Field(..., min_length=2, max_length=100)
    hashed_password: str
    
    # Role & Organization
    role: UserRole = UserRole.TEACHER
    school_id: Optional[str] = None  # School identifier
    school_name: Optional[str] = None
    district: Optional[str] = None
    block: Optional[str] = None  # Block/Taluk
    state: str = "Karnataka"
    
    # Contact
    phone: Optional[str] = None
    
    # Teaching Context
    subjects: List[str] = []  # e.g., ["Math", "Science"]
    grades: List[str] = []    # e.g., ["5", "6", "7"]
    
    # Preferences
    preferred_language: str = "en"  # en, hi, kn, etc.
    
    # Status
    is_active: bool = True
    is_verified: bool = False
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    # Statistics (for dashboard)
    total_sos_requests: int = 0
    playbooks_used: int = 0
    
    class Settings:
        """
        Beanie document settings.
        
        name: The MongoDB collection name
        use_state_management: Enable document state tracking
        """
        name = "users"
        use_state_management = True
    
    class Config:
        """Pydantic config for JSON serialization."""
        json_schema_extra = {
            "example": {
                "email": "teacher@school.gov.in",
                "name": "Priya Sharma",
                "role": "teacher",
                "school_id": "KA-BGM-001",
                "school_name": "Government Higher Primary School",
                "district": "Bangalore Urban",
                "subjects": ["Mathematics", "Science"],
                "grades": ["5", "6"],
                "preferred_language": "kn"
            }
        }
    
    def update_login(self):
        """Update the last login timestamp."""
        self.last_login = datetime.utcnow()
    
    def increment_sos_count(self):
        """Increment the SOS request counter."""
        self.total_sos_requests += 1
