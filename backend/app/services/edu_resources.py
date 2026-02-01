"""
============================================
SAHAYAK AI - Educational Resources Service
============================================

📌 WHAT IS THIS FILE?
Unified service that combines all educational resource providers:
- YouTube videos (real links via API or search fallback)
- NCERT textbooks (direct PDF links)
- DIKSHA content (app links and search)

🎓 USAGE:
    resources = await edu_resources.get_all_resources(
        subject="mathematics",
        grade="5", 
        topic="fractions"
    )
============================================
"""

from typing import Dict, Optional, List, Any
from .ncert_service import ncert_service
from .diksha_service import diksha_service
from .youtube_service import youtube_service


class EducationalResourcesService:
    """
    Unified service for all educational resources.
    Aggregates NCERT, DIKSHA, and YouTube resources.
    """
    
    def __init__(self):
        self.ncert = ncert_service
        self.diksha = diksha_service
        self.youtube = youtube_service
    
    async def get_all_resources(
        self,
        subject: str,
        grade: str,
        topic: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get all educational resources for a given context.
        
        Returns a structured dict with resources from all providers:
        - ncert: NCERT textbook links
        - diksha: DIKSHA app/web links  
        - youtube: Video links (direct or search)
        """
        resources = {
            "subject": subject,
            "grade": grade,
            "topic": topic,
        }
        
        # NCERT Resources (sync - no API call)
        ncert_resource = self.ncert.get_resource_for_context(subject, grade, topic)
        resources["ncert"] = ncert_resource
        
        # DIKSHA Resources (sync - no API call)
        diksha_resource = self.diksha.get_resource_for_context(subject, grade, topic)
        resources["diksha"] = diksha_resource
        
        # YouTube Resources (async - may call API)
        youtube_resource = await self.youtube.get_resource_for_context(subject, grade, topic)
        resources["youtube"] = youtube_resource
        
        return resources
    
    def format_for_playbook(
        self,
        resources: Dict[str, Any]
    ) -> str:
        """
        Format all resources as markdown for inclusion in playbook.
        """
        sections = []
        
        # YouTube Section
        yt = resources.get("youtube", {})
        if yt.get("available"):
            if yt.get("type") == "direct" and yt.get("videos"):
                lines = ["### 🎬 YouTube Videos (Direct Links)"]
                for i, video in enumerate(yt["videos"][:3], 1):
                    lines.append(
                        f"{i}. **[{video['title']}]({video['url']})** - {video['channel']}"
                    )
                sections.append("\n".join(lines))
            else:
                search_url = yt.get("search_url", "")
                sections.append(
                    f"### 🔍 YouTube Search\n"
                    f"[Search for related videos]({search_url})"
                )
        
        # NCERT Section
        ncert = resources.get("ncert", {})
        if ncert.get("available"):
            lines = ["### 📚 NCERT Textbook"]
            lines.append(f"- **Book**: {ncert.get('book_name', 'N/A')}")
            if ncert.get("chapter"):
                lines.append(f"- **Chapter**: {ncert['chapter']}")
            if ncert.get("pdf_url"):
                lines.append(f"- 📥 [Download PDF]({ncert['pdf_url']})")
            elif ncert.get("textbook_url"):
                lines.append(f"- 📖 [View Textbook]({ncert['textbook_url']})")
            sections.append("\n".join(lines))
        
        # DIKSHA Section
        diksha = resources.get("diksha", {})
        if diksha.get("available"):
            lines = ["### 📱 DIKSHA Resources"]
            if diksha.get("type") == "direct":
                lines.append(f"- 🎯 [Open Lesson]({diksha.get('web_url', '')})")
                if diksha.get("app_url"):
                    lines.append(f"- 📲 [Open in App]({diksha['app_url']})")
            if diksha.get("search_url"):
                lines.append(f"- 🔍 [Search More]({diksha['search_url']})")
            sections.append("\n".join(lines))
        
        return "\n\n".join(sections)
    
    def get_summary(self, resources: Dict[str, Any]) -> Dict[str, bool]:
        """
        Get a quick summary of available resources.
        """
        return {
            "has_youtube": resources.get("youtube", {}).get("available", False),
            "has_youtube_direct": resources.get("youtube", {}).get("type") == "direct",
            "has_ncert": resources.get("ncert", {}).get("available", False),
            "has_ncert_pdf": bool(resources.get("ncert", {}).get("pdf_url")),
            "has_diksha": resources.get("diksha", {}).get("available", False),
            "has_diksha_direct": resources.get("diksha", {}).get("type") == "direct",
        }


# Singleton instance
edu_resources = EducationalResourcesService()
