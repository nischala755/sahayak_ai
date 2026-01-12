"""
============================================
SAHAYAK AI - Dashboard Endpoints
============================================

📌 WHAT IS THIS FILE?
API endpoints for dashboards and analytics:
- Teacher dashboard (personal stats)
- CRP dashboard (cluster-level analytics)
- DIET dashboard (district-level analytics)
============================================
"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query

from app.schemas.schemas import (
    TeacherDashboardResponse,
    AnalyticsResponse,
    SOSResponse,
    UserResponse
)
from app.db.models.user import User, UserRole
from app.db.models.sos_request import SOSRequest, SOSStatus, ClassroomContext
from app.db.models.playbook import Playbook
from app.db.models.memory import ClassroomMemory
from app.core.dependencies import get_current_active_user, require_role
from app.services.pedagogy_engine import pedagogy_engine


router = APIRouter(prefix="/dashboard", tags=["Dashboard & Analytics"])


@router.get("/teacher", response_model=TeacherDashboardResponse)
async def get_teacher_dashboard(
    current_user: User = Depends(get_current_active_user)
):
    """
    📊 Get teacher's personal dashboard.
    
    Returns:
    - User profile
    - SOS request statistics
    - Recent SOS requests
    - Common issues
    - Successful strategies
    """
    # Get teacher stats from memory
    stats = await pedagogy_engine.get_teacher_stats(str(current_user.id))
    
    # Get recent SOS requests
    recent_sos_docs = await (
        SOSRequest
        .find(SOSRequest.teacher_id == str(current_user.id))
        .sort(-SOSRequest.created_at)
        .limit(5)
        .to_list()
    )
    
    recent_sos = [
        SOSResponse(
            id=str(sos.id),
            teacher_id=sos.teacher_id,
            teacher_name=sos.teacher_name,
            raw_input=sos.raw_input[:100] + "..." if len(sos.raw_input) > 100 else sos.raw_input,
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
        for sos in recent_sos_docs
    ]
    
    return TeacherDashboardResponse(
        user=UserResponse(
            id=str(current_user.id),
            email=current_user.email,
            name=current_user.name,
            role=current_user.role.value,
            school_id=current_user.school_id,
            school_name=current_user.school_name,
            district=current_user.district,
            subjects=current_user.subjects,
            grades=current_user.grades,
            preferred_language=current_user.preferred_language,
            is_active=current_user.is_active,
            created_at=current_user.created_at,
            total_sos_requests=current_user.total_sos_requests,
        ),
        total_sos_requests=stats["total_sos_requests"],
        total_successful_resolutions=stats["total_successful_resolutions"],
        recent_sos=recent_sos,
        top_issues=stats["top_issues"],
        subjects_taught=stats["subjects_taught"],
    )


@router.get("/crp", response_model=AnalyticsResponse)
async def get_crp_dashboard(
    current_user: User = Depends(require_role(["crp", "diet"])),
    days: int = Query(7, ge=1, le=30, description="Number of days to analyze")
):
    """
    📈 Get CRP (Cluster Resource Person) analytics dashboard.
    
    Shows aggregated data for teachers in the cluster.
    Requires CRP or DIET role.
    """
    return await _get_analytics(
        days=days,
        district=current_user.district,
        block=current_user.block,
    )


@router.get("/diet", response_model=AnalyticsResponse)
async def get_diet_dashboard(
    current_user: User = Depends(require_role(["diet"])),
    days: int = Query(7, ge=1, le=30, description="Number of days to analyze")
):
    """
    🏛️ Get DIET (District Institute of Education) analytics dashboard.
    
    Shows district-wide aggregated data.
    Requires DIET role.
    """
    return await _get_analytics(
        days=days,
        district=current_user.district,
    )


@router.get("/overview")
async def get_system_overview():
    """
    🌐 Get public system overview (for landing page).
    
    Returns high-level stats that don't require authentication.
    """
    # Get total counts
    total_users = await User.count()
    total_sos_requests = await SOSRequest.count()
    total_playbooks = await Playbook.count()
    
    # Get resolved count
    resolved_count = await SOSRequest.find(
        SOSRequest.status == SOSStatus.RESOLVED
    ).count()
    
    return {
        "total_teachers": total_users,
        "total_sos_requests": total_sos_requests,
        "total_playbooks_generated": total_playbooks,
        "successful_resolutions": resolved_count,
        "success_rate": round(resolved_count / max(total_sos_requests, 1) * 100, 1),
    }


async def _get_analytics(
    days: int,
    district: Optional[str] = None,
    block: Optional[str] = None,
) -> AnalyticsResponse:
    """
    Helper function to generate analytics data.
    """
    # Time filter
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Build query
    query_filter = {"created_at": {"$gte": start_date}}
    if district:
        query_filter["district"] = district
    
    # Get all SOS requests in range
    sos_requests = await SOSRequest.find(query_filter).to_list()
    
    # Calculate stats
    total_requests = len(sos_requests)
    
    # Issue distribution
    issue_dist = {}
    for sos in sos_requests:
        issue = sos.context_type.value if sos.context_type else "other"
        issue_dist[issue] = issue_dist.get(issue, 0) + 1
    
    # Subject distribution
    subject_dist = {}
    for sos in sos_requests:
        subject = sos.subject or "Unknown"
        subject_dist[subject] = subject_dist.get(subject, 0) + 1
    
    # Urgency distribution
    urgency_dist = {}
    for sos in sos_requests:
        urgency = sos.urgency.value if sos.urgency else "medium"
        urgency_dist[urgency] = urgency_dist.get(urgency, 0) + 1
    
    # Average resolution time
    resolution_times = [
        sos.processing_time_ms
        for sos in sos_requests
        if sos.processing_time_ms
    ]
    avg_time = sum(resolution_times) / len(resolution_times) if resolution_times else None
    
    # Daily trends
    daily_counts = {}
    for sos in sos_requests:
        day_key = sos.created_at.strftime("%Y-%m-%d")
        daily_counts[day_key] = daily_counts.get(day_key, 0) + 1
    
    daily_trends = [
        {"date": date, "count": count}
        for date, count in sorted(daily_counts.items())
    ]
    
    # Count unique teachers
    unique_teachers = len(set(sos.teacher_id for sos in sos_requests))
    
    return AnalyticsResponse(
        total_teachers=unique_teachers,
        total_sos_requests=total_requests,
        avg_resolution_time_ms=avg_time,
        issue_distribution=issue_dist,
        subject_distribution=subject_dist,
        urgency_distribution=urgency_dist,
        daily_trends=daily_trends,
    )


@router.get("/teachers", response_model=List[UserResponse])
async def list_teachers(
    current_user: User = Depends(require_role(["crp", "diet"])),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """
    👩‍🏫 List teachers (for CRP/DIET managers).
    
    Returns list of teachers in the same district.
    """
    query = User.find(User.role == UserRole.TEACHER)
    
    if current_user.district:
        query = query.find(User.district == current_user.district)
    
    teachers = await query.skip(skip).limit(limit).to_list()
    
    return [
        UserResponse(
            id=str(t.id),
            email=t.email,
            name=t.name,
            role=t.role.value,
            school_id=t.school_id,
            school_name=t.school_name,
            district=t.district,
            subjects=t.subjects,
            grades=t.grades,
            preferred_language=t.preferred_language,
            is_active=t.is_active,
            created_at=t.created_at,
            total_sos_requests=t.total_sos_requests,
        )
        for t in teachers
    ]
