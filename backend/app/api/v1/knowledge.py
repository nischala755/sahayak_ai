"""
============================================
SAHAYAK AI - Knowledge Exchange API
============================================
Teacher-to-Teacher Knowledge Sharing Endpoints
Classroom Decision Library APIs
============================================
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel, Field

from app.db.models.user import User
from app.db.models.knowledge import (
    SharedSolution, SolutionStatus, NCERTReference,
    TeacherMentorProfile, OfflinePackVersion
)
from app.core.dependencies import get_current_active_user, get_optional_user
from app.services.rag_service import rag_service


router = APIRouter(prefix="/knowledge", tags=["Knowledge Exchange"])


# ============================================
# Request/Response Schemas
# ============================================

class ShareSolutionRequest(BaseModel):
    """Request to share a classroom solution."""
    problem_description: str = Field(..., min_length=10, max_length=2000)
    solution_title: str = Field(..., min_length=5, max_length=200)
    solution_description: str = Field(..., min_length=20, max_length=5000)
    steps: List[str] = []
    materials_needed: List[str] = []
    time_required_minutes: Optional[int] = None
    subject: Optional[str] = None
    grade: Optional[str] = None
    topic: Optional[str] = None
    original_playbook_id: Optional[str] = None
    is_anonymous: bool = True
    tags: List[str] = []


class VoteSolutionRequest(BaseModel):
    """Request to vote on a solution."""
    vote: int = Field(..., ge=-1, le=1)  # -1, 0, or 1
    comment: Optional[str] = None


class SolutionResponse(BaseModel):
    """Shared solution response."""
    id: str
    teacher_name: str
    district: Optional[str]
    problem_description: str
    solution_title: str
    solution_description: str
    steps: List[str]
    materials_needed: List[str]
    time_required_minutes: Optional[int]
    subject: Optional[str]
    grade: Optional[str]
    trust_score: float
    usage_count: int
    helpful_count: int
    not_helpful_count: int
    status: str
    is_anonymous: bool
    created_at: datetime


# ============================================
# Knowledge Sharing Endpoints
# ============================================

@router.post("/share", response_model=SolutionResponse, status_code=status.HTTP_201_CREATED)
async def share_solution(
    request: ShareSolutionRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    📚 Share a classroom solution with the community.
    
    Teachers can share their successful strategies for other
    teachers to learn from and adapt.
    """
    # Create the shared solution
    solution = SharedSolution(
        teacher_id=str(current_user.id),
        teacher_name=current_user.name if not request.is_anonymous else "Anonymous Teacher",
        school_id=current_user.school_id,
        district=current_user.district,
        problem_description=request.problem_description,
        solution_title=request.solution_title,
        solution_description=request.solution_description,
        steps=request.steps,
        materials_needed=request.materials_needed,
        time_required_minutes=request.time_required_minutes,
        subject=request.subject,
        grade=request.grade,
        topic=request.topic,
        original_playbook_id=request.original_playbook_id,
        is_anonymous=request.is_anonymous,
        tags=request.tags,
        language=current_user.preferred_language
    )
    
    await solution.insert()
    
    # Add to RAG index
    rag_service.add_shared_solution(
        problem=request.problem_description,
        solution=request.solution_description,
        subject=request.subject,
        grade=request.grade
    )
    
    return _solution_to_response(solution)


@router.get("/library", response_model=List[SolutionResponse])
async def get_solution_library(
    subject: Optional[str] = Query(None),
    grade: Optional[str] = Query(None),
    sort_by: str = Query("trust_score", regex="^(trust_score|usage_count|created_at)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    📖 Browse the Classroom Decision Library.
    
    Get community-shared solutions filtered by subject, grade,
    and sorted by trust score or usage.
    """
    # Build query
    query = SharedSolution.find(
        SharedSolution.status.in_([SolutionStatus.APPROVED, SolutionStatus.FEATURED])
    )
    
    if subject:
        query = query.find(SharedSolution.subject == subject)
    if grade:
        query = query.find(SharedSolution.grade == grade)
    
    # Sort
    if sort_by == "trust_score":
        query = query.sort(-SharedSolution.trust_score)
    elif sort_by == "usage_count":
        query = query.sort(-SharedSolution.usage_count)
    else:
        query = query.sort(-SharedSolution.created_at)
    
    solutions = await query.skip(skip).limit(limit).to_list()
    
    return [_solution_to_response(s) for s in solutions]


@router.get("/library/{solution_id}", response_model=SolutionResponse)
async def get_solution(
    solution_id: str,
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    📄 Get a specific solution's details.
    
    Also increments the usage count.
    """
    solution = await SharedSolution.get(solution_id)
    
    if not solution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solution not found"
        )
    
    # Increment usage
    solution.increment_usage()
    await solution.save()
    
    return _solution_to_response(solution)


@router.post("/library/{solution_id}/vote")
async def vote_solution(
    solution_id: str,
    request: VoteSolutionRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    👍 Vote on a shared solution.
    
    Teachers can mark solutions as helpful or not helpful.
    """
    solution = await SharedSolution.get(solution_id)
    
    if not solution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solution not found"
        )
    
    # Can't vote on own solution
    if solution.teacher_id == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot vote on your own solution"
        )
    
    # Add vote
    solution.add_vote(
        teacher_id=str(current_user.id),
        teacher_name=current_user.name,
        vote=request.vote,
        comment=request.comment
    )
    
    await solution.save()
    
    return {
        "success": True,
        "new_trust_score": solution.trust_score,
        "helpful_count": solution.helpful_count,
        "not_helpful_count": solution.not_helpful_count
    }


@router.get("/my-solutions", response_model=List[SolutionResponse])
async def get_my_solutions(
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50)
):
    """
    📋 Get solutions I've shared.
    """
    solutions = await SharedSolution.find(
        SharedSolution.teacher_id == str(current_user.id)
    ).sort(-SharedSolution.created_at).skip(skip).limit(limit).to_list()
    
    return [_solution_to_response(s) for s in solutions]


# ============================================
# AI Teaching Mentor Endpoints
# ============================================

@router.get("/mentor/insights")
async def get_mentor_insights(
    current_user: User = Depends(get_current_active_user)
):
    """
    🧠 Get AI Teaching Mentor insights.
    
    Personalized insights based on teaching patterns.
    """
    profile = await TeacherMentorProfile.find_one(
        TeacherMentorProfile.teacher_id == str(current_user.id)
    )
    
    if not profile:
        # Create new profile
        profile = TeacherMentorProfile(
            teacher_id=str(current_user.id),
            teacher_name=current_user.name
        )
        await profile.insert()
    
    insights = profile.generate_insights()
    
    return {
        "teacher_name": current_user.name,
        "total_sos_requests": profile.total_sos_requests,
        "engagement_score": profile.engagement_score,
        "patterns": insights["patterns"],
        "suggestions": insights["suggestions"],
        "strengths": insights["strengths"],
        "growth_areas": insights["growth_areas"],
        "pending_nudges": profile.pending_nudges[:3],
        "last_weekly_report": profile.last_weekly_report
    }


@router.get("/mentor/weekly-report")
async def get_weekly_report(
    current_user: User = Depends(get_current_active_user)
):
    """
    📊 Get weekly progress report.
    """
    from app.services.analytics_service import analytics_service
    
    analytics = await analytics_service.get_teacher_analytics(
        teacher_id=str(current_user.id),
        days=7
    )
    
    return {
        "period": "Last 7 days",
        "summary": analytics['summary'],
        "top_subjects": list(analytics['subject_distribution'].keys())[:3],
        "daily_activity": analytics['daily_activity'],
        "mentor_insights": analytics['mentor_insights']
    }


# ============================================
# NCERT Reference Endpoints
# ============================================

@router.get("/ncert/search")
async def search_ncert_references(
    topic: str = Query(..., min_length=2),
    grade: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    limit: int = Query(5, ge=1, le=20)
):
    """
    📚 Search NCERT references by topic.
    """
    references = await NCERTReference.find_by_topic(
        topic=topic,
        grade=grade,
        subject=subject
    )
    
    return [
        {
            "class_level": ref.class_level,
            "subject": ref.subject,
            "book_name": ref.book_name,
            "chapter_number": ref.chapter_number,
            "chapter_name": ref.chapter_name,
            "topics": ref.topics,
            "learning_objectives": ref.learning_objectives,
            "page_range": f"{ref.start_page}-{ref.end_page}" if ref.start_page else None
        }
        for ref in references[:limit]
    ]


# ============================================
# Offline Pack Endpoints
# ============================================

@router.get("/offline/pack")
async def get_offline_pack(
    language: str = Query("en"),
    grade: Optional[str] = Query(None)
):
    """
    📦 Get offline knowledge pack.
    
    Download top problems and solutions for offline use.
    """
    # Get top solutions
    query = SharedSolution.find(
        SharedSolution.status == SolutionStatus.APPROVED,
        SharedSolution.trust_score >= 3.0
    )
    
    if grade:
        query = query.find(SharedSolution.grade == grade)
    
    solutions = await query.sort(-SharedSolution.trust_score).limit(50).to_list()
    
    # Get latest version
    version = await OfflinePackVersion.find_one(
        OfflinePackVersion.language == language,
        OfflinePackVersion.is_active == True
    )
    
    return {
        "version": version.version if version else "1.0.0",
        "language": language,
        "problem_count": len(solutions),
        "generated_at": datetime.utcnow().isoformat(),
        "problems": [
            {
                "id": str(s.id),
                "problem": s.problem_description,
                "solution": s.solution_description,
                "steps": s.steps,
                "subject": s.subject,
                "grade": s.grade
            }
            for s in solutions
        ]
    }


@router.post("/offline/sync")
async def sync_offline_pack(
    current_version: str = Query("1.0.0"),
    current_user: User = Depends(get_current_active_user)
):
    """
    🔄 Sync offline pack with server.
    """
    # Check for updates
    latest_version = await OfflinePackVersion.find_one(
        OfflinePackVersion.is_active == True
    )
    
    needs_update = not latest_version or latest_version.version != current_version
    
    return {
        "needs_update": needs_update,
        "latest_version": latest_version.version if latest_version else "1.0.0",
        "current_version": current_version
    }


# ============================================
# RAG Endpoints
# ============================================

@router.get("/rag/search")
async def search_knowledge_base(
    query: str = Query(..., min_length=3),
    subject: Optional[str] = Query(None),
    grade: Optional[str] = Query(None),
    limit: int = Query(5, ge=1, le=10)
):
    """
    🔍 Search the RAG knowledge base.
    
    Find relevant documents from shared solutions and NCERT references.
    """
    context, sources = rag_service.get_augmented_context(
        query=query,
        subject=subject,
        grade=grade
    )
    
    return {
        "query": query,
        "sources": sources[:limit],
        "context_preview": context[:500] if context else None
    }


@router.get("/rag/stats")
async def get_rag_stats():
    """
    📈 Get RAG system statistics.
    """
    return rag_service.get_stats()


# ============================================
# Helper Functions
# ============================================

def _solution_to_response(solution: SharedSolution) -> SolutionResponse:
    """Convert SharedSolution to response model."""
    return SolutionResponse(
        id=str(solution.id),
        teacher_name=solution.teacher_name if not solution.is_anonymous else f"Teacher from {solution.district or 'India'}",
        district=solution.district if not solution.is_anonymous else None,
        problem_description=solution.problem_description,
        solution_title=solution.solution_title,
        solution_description=solution.solution_description,
        steps=solution.steps,
        materials_needed=solution.materials_needed,
        time_required_minutes=solution.time_required_minutes,
        subject=solution.subject,
        grade=solution.grade,
        trust_score=solution.trust_score,
        usage_count=solution.usage_count,
        helpful_count=solution.helpful_count,
        not_helpful_count=solution.not_helpful_count,
        status=solution.status.value,
        is_anonymous=solution.is_anonymous,
        created_at=solution.created_at
    )
