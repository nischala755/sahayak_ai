"""
============================================
SAHAYAK AI - Analytics Service
============================================
Advanced analytics for dashboards with
interactive visualizations data.
============================================
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import Counter

from app.db.models.sos_request import SOSRequest, SOSStatus, ContextType
from app.db.models.playbook import Playbook
from app.db.models.user import User, UserRole
from app.db.models.knowledge import SharedSolution, TeacherMentorProfile


class AnalyticsService:
    """
    Advanced analytics service for role-based dashboards.
    Provides data for visualizations and insights.
    """
    
    # ============================================
    # TEACHER DASHBOARD ANALYTICS
    # ============================================
    
    async def get_teacher_analytics(
        self,
        teacher_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get comprehensive teacher analytics."""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get teacher's SOS requests
        sos_requests = await SOSRequest.find(
            SOSRequest.teacher_id == teacher_id,
            SOSRequest.created_at >= start_date
        ).to_list()
        
        # Get saved/favorited playbooks
        saved_playbooks = await Playbook.find(
            Playbook.sos_request_id.in_([str(sos.id) for sos in sos_requests]),
            Playbook.was_implemented == True
        ).to_list()
        
        # Get or create mentor profile
        mentor_profile = await TeacherMentorProfile.find_one(
            TeacherMentorProfile.teacher_id == teacher_id
        )
        
        # Calculate analytics
        total_sos = len(sos_requests)
        resolved = sum(1 for sos in sos_requests if sos.status == SOSStatus.RESOLVED)
        
        # Subject distribution
        subjects = Counter(sos.subject for sos in sos_requests if sos.subject)
        
        # Issue type distribution
        issues = Counter(
            sos.context_type.value if sos.context_type else 'other'
            for sos in sos_requests
        )
        
        # Daily activity trend
        daily_activity = {}
        for sos in sos_requests:
            day = sos.created_at.strftime("%Y-%m-%d")
            daily_activity[day] = daily_activity.get(day, 0) + 1
        
        # Weekly pattern (for heatmap)
        hour_day_matrix = [[0 for _ in range(7)] for _ in range(24)]
        for sos in sos_requests:
            hour = sos.created_at.hour
            day = sos.created_at.weekday()
            hour_day_matrix[hour][day] += 1
        
        return {
            'summary': {
                'total_sos': total_sos,
                'resolved': resolved,
                'resolution_rate': round(resolved / max(total_sos, 1) * 100, 1),
                'saved_playbooks': len(saved_playbooks),
                'days_analyzed': days
            },
            'subject_distribution': dict(subjects.most_common(6)),
            'issue_distribution': dict(issues.most_common(6)),
            'daily_activity': [
                {'date': d, 'count': c}
                for d, c in sorted(daily_activity.items())
            ],
            'weekly_heatmap': hour_day_matrix,
            'mentor_insights': mentor_profile.generate_insights() if mentor_profile else None,
            'recent_playbooks': [
                {
                    'id': str(p.id),
                    'title': p.title,
                    'created_at': p.created_at.isoformat()
                }
                for p in saved_playbooks[:5]
            ]
        }
    
    async def get_teacher_shared_solutions(
        self,
        teacher_id: str
    ) -> List[Dict]:
        """Get solutions shared by this teacher."""
        solutions = await SharedSolution.find(
            SharedSolution.teacher_id == teacher_id
        ).sort(-SharedSolution.created_at).limit(20).to_list()
        
        return [
            {
                'id': str(s.id),
                'title': s.solution_title,
                'problem': s.problem_description[:100],
                'trust_score': s.trust_score,
                'usage_count': s.usage_count,
                'status': s.status.value
            }
            for s in solutions
        ]
    
    # ============================================
    # CRP DASHBOARD ANALYTICS
    # ============================================
    
    async def get_crp_analytics(
        self,
        district: str = None,
        block: str = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get cluster-level analytics for CRP dashboard."""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Build filter
        query = {'created_at': {'$gte': start_date}}
        if district:
            # We need to join with users to filter by district
            # For now, get all and filter
            pass
        
        # Get all SOS requests in range
        all_sos = await SOSRequest.find(
            SOSRequest.created_at >= start_date
        ).to_list()
        
        # Get teachers in cluster
        teacher_query = User.find(User.role == UserRole.TEACHER)
        if district:
            teacher_query = teacher_query.find(User.district == district)
        if block:
            teacher_query = teacher_query.find(User.block == block)
        
        teachers = await teacher_query.to_list()
        teacher_ids = set(str(t.id) for t in teachers)
        
        # Filter SOS by cluster teachers
        cluster_sos = [sos for sos in all_sos if sos.teacher_id in teacher_ids]
        
        # Most frequent problems
        problem_freq = Counter()
        for sos in cluster_sos:
            key = f"{sos.subject or 'General'} - {sos.context_type.value if sos.context_type else 'other'}"
            problem_freq[key] += 1
        
        # Teacher engagement metrics
        active_teachers = set(sos.teacher_id for sos in cluster_sos)
        engagement_rate = len(active_teachers) / max(len(teachers), 1) * 100
        
        # Get proven solutions from cluster
        proven_solutions = await SharedSolution.find(
            SharedSolution.status == "approved",
            SharedSolution.trust_score >= 3.0
        ).sort(-SharedSolution.trust_score).limit(10).to_list()
        
        # Issue trends over time
        date_issue_counts = {}
        for sos in cluster_sos:
            date = sos.created_at.strftime("%Y-%m-%d")
            issue = sos.context_type.value if sos.context_type else 'other'
            if date not in date_issue_counts:
                date_issue_counts[date] = {}
            date_issue_counts[date][issue] = date_issue_counts[date].get(issue, 0) + 1
        
        return {
            'summary': {
                'total_teachers': len(teachers),
                'active_teachers': len(active_teachers),
                'engagement_rate': round(engagement_rate, 1),
                'total_sos': len(cluster_sos),
                'days_analyzed': days
            },
            'frequent_problems': [
                {'problem': k, 'count': v}
                for k, v in problem_freq.most_common(10)
            ],
            'proven_solutions': [
                {
                    'id': str(s.id),
                    'title': s.solution_title,
                    'subject': s.subject,
                    'trust_score': s.trust_score,
                    'usage_count': s.usage_count
                }
                for s in proven_solutions
            ],
            'issue_trends': [
                {'date': d, **counts}
                for d, counts in sorted(date_issue_counts.items())
            ],
            'teacher_leaderboard': await self._get_teacher_leaderboard(teacher_ids)
        }
    
    async def _get_teacher_leaderboard(
        self,
        teacher_ids: set,
        limit: int = 10
    ) -> List[Dict]:
        """Get top contributing teachers."""
        # Count contributions
        contributions = {}
        
        solutions = await SharedSolution.find(
            SharedSolution.teacher_id.in_(list(teacher_ids))
        ).to_list()
        
        for sol in solutions:
            tid = sol.teacher_id
            if tid not in contributions:
                contributions[tid] = {'solutions': 0, 'helpful_votes': 0}
            contributions[tid]['solutions'] += 1
            contributions[tid]['helpful_votes'] += sol.helpful_count
        
        # Get teacher names
        teachers = await User.find(
            User.id.in_([t for t in contributions.keys()])
        ).to_list()
        
        teacher_names = {str(t.id): t.name for t in teachers}
        
        # Build leaderboard
        leaderboard = []
        for tid, stats in contributions.items():
            score = stats['solutions'] * 10 + stats['helpful_votes'] * 2
            leaderboard.append({
                'teacher_id': tid,
                'teacher_name': teacher_names.get(tid, 'Anonymous'),
                'solutions_shared': stats['solutions'],
                'helpful_votes': stats['helpful_votes'],
                'score': score
            })
        
        return sorted(leaderboard, key=lambda x: x['score'], reverse=True)[:limit]
    
    # ============================================
    # DIET DASHBOARD ANALYTICS
    # ============================================
    
    async def get_diet_analytics(
        self,
        district: str = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get district-level analytics for DIET dashboard."""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get all teachers in district
        teacher_query = User.find(User.role == UserRole.TEACHER)
        if district:
            teacher_query = teacher_query.find(User.district == district)
        
        teachers = await teacher_query.to_list()
        teacher_ids = set(str(t.id) for t in teachers)
        
        # Get all SOS requests
        all_sos = await SOSRequest.find(
            SOSRequest.created_at >= start_date
        ).to_list()
        
        district_sos = [sos for sos in all_sos if sos.teacher_id in teacher_ids]
        
        # District heatmap data (block-wise)
        block_data = {}
        for teacher in teachers:
            block = teacher.block or 'Unknown'
            if block not in block_data:
                block_data[block] = {'teachers': 0, 'sos_count': 0}
            block_data[block]['teachers'] += 1
        
        for sos in district_sos:
            teacher = next((t for t in teachers if str(t.id) == sos.teacher_id), None)
            if teacher:
                block = teacher.block or 'Unknown'
                block_data[block]['sos_count'] += 1
        
        # FLN concept gaps analysis
        fln_issues = {
            'reading_comprehension': 0,
            'basic_numeracy': 0,
            'writing_skills': 0,
            'oral_expression': 0
        }
        
        # Map context types to FLN areas
        fln_mapping = {
            'concept_confusion': 'basic_numeracy',
            'reading_issue': 'reading_comprehension',
            'writing_difficulty': 'writing_skills',
            'communication': 'oral_expression'
        }
        
        for sos in district_sos:
            if sos.context_type:
                fln_area = fln_mapping.get(sos.context_type.value)
                if fln_area:
                    fln_issues[fln_area] += 1
        
        # Training need indicators
        subject_struggles = Counter(sos.subject for sos in district_sos if sos.subject)
        grade_struggles = Counter(sos.grade for sos in district_sos if sos.grade)
        
        training_needs = []
        for subject, count in subject_struggles.most_common(5):
            if count >= 5:  # Threshold for training need
                training_needs.append({
                    'area': subject,
                    'type': 'subject',
                    'incident_count': count,
                    'priority': 'high' if count >= 20 else 'medium'
                })
        
        return {
            'summary': {
                'total_teachers': len(teachers),
                'total_blocks': len(block_data),
                'total_sos': len(district_sos),
                'avg_sos_per_teacher': round(len(district_sos) / max(len(teachers), 1), 1),
                'days_analyzed': days
            },
            'block_heatmap': [
                {
                    'block': block,
                    'teachers': data['teachers'],
                    'sos_count': data['sos_count'],
                    'intensity': data['sos_count'] / max(data['teachers'], 1)
                }
                for block, data in block_data.items()
            ],
            'fln_gaps': fln_issues,
            'training_needs': training_needs,
            'subject_distribution': dict(subject_struggles.most_common(8)),
            'grade_distribution': dict(grade_struggles.most_common(10)),
            'exportable_summary': await self._generate_export_summary(
                teachers, district_sos, block_data, training_needs
            )
        }
    
    async def _generate_export_summary(
        self,
        teachers: List,
        sos_requests: List,
        block_data: Dict,
        training_needs: List
    ) -> Dict:
        """Generate exportable summary for DIET reports."""
        return {
            'generated_at': datetime.utcnow().isoformat(),
            'total_teachers': len(teachers),
            'total_sos_requests': len(sos_requests),
            'blocks_analyzed': len(block_data),
            'top_training_needs': training_needs[:3],
            'key_insights': [
                f"{len(sos_requests)} classroom issues handled in analysis period",
                f"{len(training_needs)} training priority areas identified",
                f"Highest activity in {max(block_data.items(), key=lambda x: x[1]['sos_count'])[0] if block_data else 'N/A'}"
            ]
        }


# Singleton instance
analytics_service = AnalyticsService()
