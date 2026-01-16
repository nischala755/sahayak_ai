"""
============================================
SAHAYAK AI - SOS Endpoints
============================================

📌 WHAT IS THIS FILE?
The core API for the SOS feature - teachers submit
classroom emergencies and receive AI-generated playbooks.

🎓 LEARNING POINT:
This is the heart of SAHAYAK AI:
1. Teacher submits problem (text or voice transcript)
2. System extracts context
3. AI generates playbook
4. Playbook is returned to teacher
============================================
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query, BackgroundTasks

from app.schemas.schemas import (
    SOSCreate,
    SOSResponse,
    SOSWithPlaybook,
    PlaybookResponse,
    PlaybookFeedback,
    Message
)
from app.db.models.user import User
from app.db.models.sos_request import SOSRequest, SOSStatus
from app.db.models.playbook import Playbook
from app.core.dependencies import get_current_active_user, get_optional_user
from app.services.pedagogy_engine import pedagogy_engine


router = APIRouter(prefix="/sos", tags=["SOS - Classroom Emergency"])


@router.post("/", response_model=SOSWithPlaybook, status_code=status.HTTP_201_CREATED)
async def create_sos_request(
    sos_data: SOSCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    🆘 Submit an SOS request for classroom help.
    
    This is the main endpoint for teachers to get instant help.
    The system will:
    1. Accept your description of the classroom problem
    2. Automatically extract context (subject, grade, etc.)
    3. Generate an AI-powered teaching rescue playbook
    4. Return actionable steps you can use immediately
    
    **Example Request:**
    ```json
    {
        "raw_input": "Students in my class 5 math class are not understanding fractions",
        "input_type": "text",
        "input_language": "en"
    }
    ```
    """
    # Create SOS request
    sos_request = SOSRequest(
        teacher_id=str(current_user.id),
        teacher_name=current_user.name,
        raw_input=sos_data.raw_input,
        input_type=sos_data.input_type,
        input_language=sos_data.input_language,
        subject=sos_data.subject,
        grade=sos_data.grade,
        topic=sos_data.topic,
        school_id=current_user.school_id,
        district=current_user.district,
    )
    
    await sos_request.insert()
    
    # Update user's SOS count
    current_user.increment_sos_count()
    await current_user.save()
    
    # Process with AI (generate playbook)
    result = await pedagogy_engine.process_sos_request(sos_request)
    
    # Reload SOS request to get updated data
    sos_request = await SOSRequest.get(sos_request.id)
    
    # Build response
    response = SOSWithPlaybook(
        id=str(sos_request.id),
        teacher_id=sos_request.teacher_id,
        teacher_name=sos_request.teacher_name,
        raw_input=sos_request.raw_input,
        input_type=sos_request.input_type,
        subject=sos_request.subject,
        grade=sos_request.grade,
        topic=sos_request.topic,
        urgency=sos_request.urgency.value if sos_request.urgency else "medium",
        status=sos_request.status.value,
        created_at=sos_request.created_at,
        playbook_id=sos_request.playbook_id,
        processing_time_ms=sos_request.processing_time_ms,
        playbook=None
    )
    
    # Include playbook if generated
    if result.get("success") and result.get("playbook"):
        playbook = result["playbook"]
        response.playbook = {
            "id": str(playbook.id),
            "title": playbook.title,
            "summary": playbook.summary,
            "immediate_actions": playbook.immediate_actions,
            "recovery_steps": [
                {
                    "step_number": step.step_number,
                    "action": step.action,
                    "duration_minutes": step.duration_minutes,
                }
                for step in playbook.recovery_steps
            ],
            "alternatives": playbook.alternatives,
            "success_indicators": playbook.success_indicators,
            "youtube_videos": [
                {"title": v.title, "url": v.url, "description": v.description}
                for v in playbook.youtube_videos
            ] if playbook.youtube_videos else [],
            "teaching_resources": [
                {"title": r.title, "url": r.url, "resource_type": r.resource_type, "description": r.description}
                for r in playbook.teaching_resources
            ] if playbook.teaching_resources else [],
            "teaching_tips": playbook.teaching_tips or [],
            "ncert_reference": playbook.ncert_reference,
            "estimated_time_minutes": playbook.estimated_time_minutes,
            "difficulty_level": playbook.difficulty_level,
        }
    
    return response


@router.post("/quick", response_model=dict)
async def quick_sos(
    raw_input: str = Query(..., min_length=5, max_length=2000, description="Describe your classroom problem"),
    subject: Optional[str] = Query(None, description="Subject being taught"),
    grade: Optional[str] = Query(None, description="Class/Grade level"),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    🚀 Quick SOS - Get help without full authentication.
    
    A simplified endpoint for quick help. Can be used:
    - With authentication (tracked to user)
    - Without authentication (anonymous, for demos)
    
    This is perfect for prototype demonstrations.
    """
    teacher_id = str(current_user.id) if current_user else "anonymous"
    teacher_name = current_user.name if current_user else "Anonymous Teacher"
    
    # Create SOS request
    sos_request = SOSRequest(
        teacher_id=teacher_id,
        teacher_name=teacher_name,
        raw_input=raw_input,
        input_type="text",
        input_language="en",
        subject=subject,
        grade=grade,
    )
    
    await sos_request.insert()
    
    # Process with AI
    result = await pedagogy_engine.process_sos_request(sos_request)
    
    if result.get("success") and result.get("playbook"):
        playbook = result["playbook"]
        return {
            "success": True,
            "sos_id": str(sos_request.id),
            "problem": raw_input,
            "detected_subject": sos_request.subject,
            "detected_grade": sos_request.grade,
            "urgency": sos_request.urgency.value if sos_request.urgency else "medium",
            "playbook": {
                "title": playbook.title,
                "summary": playbook.summary,
                "immediate_actions": playbook.immediate_actions,
                "recovery_steps": [
                    {"step": step.step_number, "action": step.action, "minutes": step.duration_minutes}
                    for step in playbook.recovery_steps
                ],
                "alternatives": playbook.alternatives,
                "success_indicators": playbook.success_indicators,
                "youtube_videos": [
                    {"title": v.title, "url": v.url, "description": v.description}
                    for v in playbook.youtube_videos
                ] if playbook.youtube_videos else [],
                "teaching_resources": [
                    {"title": r.title, "url": r.url, "resource_type": r.resource_type, "description": r.description}
                    for r in playbook.teaching_resources
                ] if playbook.teaching_resources else [],
                "teaching_tips": playbook.teaching_tips or [],
                "ncert_reference": playbook.ncert_reference,
                "time_minutes": playbook.estimated_time_minutes,
                "difficulty": playbook.difficulty_level,
            },
            "processing_time_ms": sos_request.processing_time_ms,
        }
    else:
        return {
            "success": False,
            "error": result.get("error", "Failed to generate playbook"),
        }


@router.get("/", response_model=List[SOSResponse])
async def get_my_sos_requests(
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    status_filter: Optional[str] = Query(None, description="Filter by status: pending, processing, resolved, failed")
):
    """
    📋 Get your SOS request history.
    
    Returns a list of your past SOS requests with their status.
    """
    query = SOSRequest.find(SOSRequest.teacher_id == str(current_user.id))
    
    if status_filter:
        try:
            status_enum = SOSStatus(status_filter)
            query = query.find(SOSRequest.status == status_enum)
        except ValueError:
            pass
    
    sos_requests = await query.sort(-SOSRequest.created_at).skip(skip).limit(limit).to_list()
    
    return [
        SOSResponse(
            id=str(sos.id),
            teacher_id=sos.teacher_id,
            teacher_name=sos.teacher_name,
            raw_input=sos.raw_input,
            input_type=sos.input_type,
            subject=sos.subject,
            grade=sos.grade,
            topic=sos.topic,
            urgency=sos.urgency.value if sos.urgency else "medium",
            status=sos.status.value,
            created_at=sos.created_at,
            playbook_id=sos.playbook_id,
            processing_time_ms=sos.processing_time_ms,
        )
        for sos in sos_requests
    ]


@router.get("/{sos_id}", response_model=SOSWithPlaybook)
async def get_sos_request(
    sos_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    📖 Get a specific SOS request with its playbook.
    """
    sos = await SOSRequest.get(sos_id)
    
    if not sos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SOS request not found"
        )
    
    # Check ownership (or admin access)
    if sos.teacher_id != str(current_user.id) and current_user.role.value not in ["crp", "diet"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this SOS request"
        )
    
    # Get playbook if exists
    playbook_data = None
    if sos.playbook_id:
        playbook = await Playbook.get(sos.playbook_id)
        if playbook:
            playbook.record_view()
            await playbook.save()
            
            playbook_data = {
                "id": str(playbook.id),
                "title": playbook.title,
                "summary": playbook.summary,
                "immediate_actions": playbook.immediate_actions,
                "recovery_steps": [
                    {
                        "step_number": step.step_number,
                        "action": step.action,
                        "duration_minutes": step.duration_minutes,
                        "teacher_dialogue": step.teacher_dialogue,
                        "expected_outcome": step.expected_outcome,
                    }
                    for step in playbook.recovery_steps
                ],
                "alternatives": playbook.alternatives,
                "success_indicators": playbook.success_indicators,
                "estimated_time_minutes": playbook.estimated_time_minutes,
                "difficulty_level": playbook.difficulty_level,
            }
    
    return SOSWithPlaybook(
        id=str(sos.id),
        teacher_id=sos.teacher_id,
        teacher_name=sos.teacher_name,
        raw_input=sos.raw_input,
        input_type=sos.input_type,
        subject=sos.subject,
        grade=sos.grade,
        topic=sos.topic,
        urgency=sos.urgency.value if sos.urgency else "medium",
        status=sos.status.value,
        created_at=sos.created_at,
        playbook_id=sos.playbook_id,
        processing_time_ms=sos.processing_time_ms,
        playbook=playbook_data
    )


@router.post("/{sos_id}/feedback", response_model=Message)
async def submit_sos_feedback(
    sos_id: str,
    feedback: PlaybookFeedback,
    current_user: User = Depends(get_current_active_user)
):
    """
    ⭐ Submit feedback on an SOS/playbook.
    
    Your feedback helps improve SAHAYAK AI's recommendations!
    """
    sos = await SOSRequest.get(sos_id)
    
    if not sos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SOS request not found"
        )
    
    if sos.teacher_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to give feedback on this request"
        )
    
    # Update SOS with feedback
    sos.was_helpful = feedback.was_helpful
    sos.feedback_rating = feedback.effectiveness_rating
    sos.feedback_text = feedback.feedback_text
    await sos.save()
    
    # Update playbook if exists
    if sos.playbook_id:
        playbook = await Playbook.get(sos.playbook_id)
        if playbook:
            playbook.was_implemented = feedback.was_helpful
            playbook.effectiveness_rating = feedback.effectiveness_rating
            await playbook.save()
    
    return Message(message="Thank you for your feedback!")
