"""
============================================
SAHAYAK AI - Pedagogy Engine
============================================

📌 WHAT IS THIS FILE?
The main orchestration layer that:
1. Takes a teacher's SOS request
2. Extracts context
3. Calls Gemini for playbook generation
4. Structures the response
5. Stores in database

🎓 LEARNING POINT:
This is the "business logic" layer - it coordinates
multiple services to fulfill a user request.
============================================
"""

import re
from datetime import datetime
from typing import Dict, Any, Optional

from app.services.gemini_service import gemini_service
from app.services.context_engine import context_engine
from app.services.redis_cache import redis_cache
from app.services.edu_resources import edu_resources
from app.db.models.sos_request import SOSRequest, SOSStatus
from app.db.models.playbook import Playbook, PlaybookAction, VideoResource, TeachingResource
from app.db.models.memory import ClassroomMemory


class PedagogyEngine:
    """
    Main pedagogical coaching engine.
    
    Orchestrates the full flow from teacher request to playbook delivery.
    """
    
    async def process_sos_request(
        self,
        sos_request: SOSRequest
    ) -> Dict[str, Any]:
        """
        Process an SOS request and generate a teaching playbook.
        
        Args:
            sos_request: The saved SOS request document
        
        Returns:
            Dict containing the generated playbook and metadata
        
        Flow:
        1. Extract context from raw input
        2. Update SOS request with context
        3. Generate playbook via Gemini
        4. Parse and structure response
        5. Save playbook
        6. Update SOS request with playbook reference
        """
        try:
            # Mark as processing
            sos_request.start_processing()
            await sos_request.save()
            
            # Step 1: Extract context from raw input
            extracted_context = context_engine.extract_context(sos_request.raw_input)
            
            # Step 2: Update SOS with context - PRESERVE user-provided values
            # Only use extracted values if user didn't provide them
            sos_request.subject = sos_request.subject or extracted_context.get("subject")
            sos_request.grade = sos_request.grade or extracted_context.get("grade")
            sos_request.topic = extracted_context.get("topic")  # Topic always from extraction
            sos_request.context_type = extracted_context.get("context_type")
            sos_request.urgency = extracted_context.get("urgency")
            sos_request.student_count = extracted_context.get("student_count")
            sos_request.specific_challenge = extracted_context.get("specific_challenge")
            await sos_request.save()
            
            # Step 3: Build context dict for Gemini
            classroom_context = {
                "subject": sos_request.subject or "General",
                "grade": sos_request.grade or "Mixed",
                "topic": sos_request.topic or "General Topic",
                "student_count": sos_request.student_count or 30,
                "urgency": sos_request.urgency.value if sos_request.urgency else "medium",
                # Map language code to full name for Gemini
                "language": {"hi": "Hindi", "kn": "Kannada", "en": "English"}.get(
                    sos_request.input_language, "English"
                ),
            }
            
            # Step 4: Check Redis cache using SEMANTIC matching (keywords, not hash)
            language_name = classroom_context["language"]
            cached_response = await redis_cache.get_cached_playbook(
                subject=sos_request.subject,
                grade=sos_request.grade,
                topic=sos_request.topic,  # Key for semantic matching!
                language=language_name
            )
            
            # Track if response is from cache
            from_cache = False
            cache_timestamp = None
            
            if cached_response:
                # Cache hit - use cached AI response
                print(f"⚡ SEMANTIC CACHE HIT for: {sos_request.subject}/{sos_request.grade}/{sos_request.topic}")
                ai_response = cached_response
                from_cache = True
                cache_timestamp = cached_response.get("cached_at")
            else:
                # Cache miss - call Gemini AI
                print(f"🤖 Calling Gemini AI for: {sos_request.subject}/{sos_request.grade}/{sos_request.topic}")
                ai_response = await gemini_service.generate_playbook(
                    problem_description=sos_request.raw_input,
                    classroom_context=classroom_context
                )
                
                # Cache the response using semantic key (subject/grade/topic)
                if ai_response.get("text"):
                    await redis_cache.cache_playbook(
                        response=ai_response,
                        subject=sos_request.subject,
                        grade=sos_request.grade,
                        topic=sos_request.topic,
                        language=language_name
                    )
            
            # Step 5: Fetch real educational resources (YouTube, NCERT, DIKSHA)
            educational_resources = await edu_resources.get_all_resources(
                subject=sos_request.subject or "General",
                grade=sos_request.grade or "5",
                topic=sos_request.topic
            )
            
            # Step 6: Parse and structure the response
            playbook = await self._create_playbook(
                sos_request=sos_request,
                ai_response=ai_response,
                edu_resources=educational_resources
            )
            
            # Step 7: Update SOS with playbook reference
            sos_request.complete_processing(str(playbook.id))
            await sos_request.save()
            
            # Update classroom memory
            await self._update_memory(sos_request)
            
            return {
                "success": True,
                "playbook": playbook,
                "processing_time_ms": sos_request.processing_time_ms,
                "from_cache": from_cache,
                "cache_timestamp": cache_timestamp,
            }
            
        except Exception as e:
            sos_request.mark_failed()
            await sos_request.save()
            
            return {
                "success": False,
                "error": str(e),
            }
    
    async def _create_playbook(
        self,
        sos_request: SOSRequest,
        ai_response: Dict[str, Any],
        edu_resources: Optional[Dict[str, Any]] = None
    ) -> Playbook:
        """
        Create and save a playbook from AI response.
        
        Parses the markdown response from Gemini and structures
        it into a proper Playbook document. Uses real educational
        resources fetched from APIs when available.
        """
        response_text = ai_response.get("text", "")
        
        # Parse the response
        parsed = self._parse_playbook_response(response_text)
        
        # Override YouTube videos with real API results if available
        youtube_videos = parsed.get("youtube_videos", [])
        if edu_resources and edu_resources.get("youtube"):
            yt = edu_resources["youtube"]
            if yt.get("type") == "direct" and yt.get("videos"):
                youtube_videos = [
                    {
                        "title": v.get("title", ""),
                        "url": v.get("url", ""),
                        "description": f"Channel: {v.get('channel', 'Educational')}",  # Put channel in description
                        "duration": None  # API doesn't return duration
                    }
                    for v in yt["videos"]
                ]
            else:
                # Add search fallback
                youtube_videos = [{
                    "title": f"🔍 Search YouTube: {sos_request.topic or 'topic'} class {sos_request.grade or ''}",
                    "url": yt.get("search_url", ""),
                    "description": "Click to search for related educational videos",
                    "duration": None
                }]
        
        # Build NCERT reference from real data (model expects string, not dict)
        ncert_reference = parsed.get("ncert_reference")
        if edu_resources and edu_resources.get("ncert", {}).get("available"):
            ncert = edu_resources["ncert"]
            # Format as string with URL for display
            book_name = ncert.get("book_name", "NCERT Textbook")
            chapter = ncert.get("chapter")
            pdf_url = ncert.get("pdf_url") or ncert.get("textbook_url", "")
            
            if chapter:
                ncert_reference = f"{book_name} Chapter {chapter} | PDF: {pdf_url}"
            else:
                ncert_reference = f"{book_name} | Link: {pdf_url}"
        
        # Build teaching resources with real DIKSHA links
        teaching_resources = parsed.get("teaching_resources", [])
        if edu_resources and edu_resources.get("diksha", {}).get("available"):
            diksha = edu_resources["diksha"]
            diksha_resource = {
                "title": f"DIKSHA: {sos_request.topic or 'Learning Resources'}",  # Required field
                "url": diksha.get("web_url", ""),
                "resource_type": "diksha",  # Required field
                "description": diksha.get("text", ""),
            }
            # Add to beginning of resources
            teaching_resources = [diksha_resource] + teaching_resources
        
        # Create playbook document
        playbook = Playbook(
            sos_request_id=str(sos_request.id),
            title=parsed.get("title", "Teaching Rescue Playbook"),
            summary=parsed.get("summary", "AI-generated teaching strategy"),
            immediate_actions=parsed.get("immediate_actions", []),
            recovery_steps=parsed.get("recovery_steps", []),
            alternatives=parsed.get("alternatives", []),
            success_indicators=parsed.get("success_indicators", []),
            youtube_videos=youtube_videos,
            teaching_resources=teaching_resources,
            teaching_tips=parsed.get("teaching_tips", []),
            ncert_reference=ncert_reference,
            estimated_time_minutes=parsed.get("estimated_time", 10),
            difficulty_level=parsed.get("difficulty", "medium"),
            model_used="gemini-2.5-flash",
            prompt_tokens=ai_response.get("prompt_tokens"),
            response_tokens=ai_response.get("response_tokens"),
            language=sos_request.input_language,
        )
        
        await playbook.insert()
        return playbook
    
    def _parse_playbook_response(self, text: str) -> Dict[str, Any]:
        """
        Parse the markdown response from Gemini into structured data.
        """
        result = {
            "title": "Teaching Rescue Playbook",
            "summary": "",
            "immediate_actions": [],
            "recovery_steps": [],
            "alternatives": [],
            "success_indicators": [],
            "youtube_videos": [],
            "teaching_resources": [],
            "teaching_tips": [],
            "ncert_reference": None,
            "estimated_time": 10,
            "difficulty": "medium",
        }
        
        if not text or len(text) < 50:
            print("Warning: AI response too short or empty")
            return result
        
        print(f"Parsing AI response ({len(text)} chars)...")
        
        # Extract title (more flexible matching)
        title_patterns = [
            r'###?\s*(?:🎯\s*)?Title\s*\n\s*(.+?)(?:\n|$)',
            r'^##?\s+(.+?)(?:\n|$)',  # Match first heading
            r'\*\*Title[:\s]*\*\*\s*(.+?)(?:\n|$)',
        ]
        for pattern in title_patterns:
            title_match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if title_match:
                result["title"] = title_match.group(1).strip()[:200]
                break
        
        # Extract summary (more flexible)
        summary_patterns = [
            r'###?\s*(?:📋\s*)?Summary\s*\n(.+?)(?=\n###?|\n\*\*Step|\n\*\*Immediate|$)',
            r'Summary[:\s]*\n(.+?)(?=\n###?|\n\*\*|$)',
        ]
        for pattern in summary_patterns:
            summary_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if summary_match:
                result["summary"] = summary_match.group(1).strip()[:500]
                break
        
        # Extract immediate actions (numbered list OR bullet list)
        immediate_patterns = [
            r'###?\s*(?:⚡\s*)?Immediate Actions[^\n]*\n((?:[\d]+[\.:\)].+\n?)+)',
            r'Immediate Actions[^\n]*\n((?:[\d]+[\.:\)].+\n?)+)',
            r'###?\s*(?:⚡\s*)?Immediate Actions[^\n]*\n((?:[-•*]\s*.+\n?)+)',
            r'Do\s*(?:NOW|RIGHT\s*NOW)[^\n]*\n((?:[\d]+[\.:\)].+\n?)+)',
            r'Do\s*(?:NOW|RIGHT\s*NOW)[^\n]*\n((?:[-•*]\s*.+\n?)+)',
        ]
        for pattern in immediate_patterns:
            immediate_match = re.search(pattern, text, re.IGNORECASE)
            if immediate_match:
                content = immediate_match.group(1)
                # Try numbered first
                actions = re.findall(r'[\d]+[\.:\)]\s*(.+?)(?:\n|$)', content)
                if not actions:
                    # Try bullet points
                    actions = re.findall(r'[-•*]\s*(.+?)(?:\n|$)', content)
                result["immediate_actions"] = [a.strip() for a in actions[:5] if a.strip() and len(a.strip()) > 5]
                break
        
        # Extract alternatives
        alt_patterns = [
            r'###?\s*(?:🔄\s*)?Alternative[^\n]*\n((?:[\d]+[\.\)].+\n?)+)',
            r'Alternative[^\n]*\n((?:[\d]+[\.\)].+\n?)+)',
        ]
        for pattern in alt_patterns:
            alt_match = re.search(pattern, text, re.IGNORECASE)
            if alt_match:
                alts = re.findall(r'[\d]+[\.\)]\s*(.+?)(?:\n|$)', alt_match.group(1))
                result["alternatives"] = [a.strip() for a in alts[:3] if a.strip()]
                break
        
        # Extract success indicators (bullet list)
        success_patterns = [
            r'###?\s*(?:✅\s*)?Success Indicators[^\n]*\n((?:[-•*]\s*.+\n?)+)',
            r'Success Indicators[^\n]*\n((?:[-•*]\s*.+\n?)+)',
        ]
        for pattern in success_patterns:
            success_match = re.search(pattern, text, re.IGNORECASE)
            if success_match:
                indicators = re.findall(r'[-•*]\s*(.+?)(?:\n|$)', success_match.group(1))
                result["success_indicators"] = [i.strip() for i in indicators[:5] if i.strip()]
                break
        
        # Extract time estimate
        time_match = re.search(r'Time(?:\s+Estimate)?[:\s]+(\d+)\s*(?:min|minutes)?', text, re.IGNORECASE)
        if time_match:
            result["estimated_time"] = min(int(time_match.group(1)), 45)
        
        # Extract difficulty
        diff_match = re.search(r'Difficulty[:\s]+(\w+)', text, re.IGNORECASE)
        if diff_match:
            diff = diff_match.group(1).lower()
            if diff in ["easy", "medium", "hard"]:
                result["difficulty"] = diff
        
        # Parse recovery steps (multiple formats)
        step_patterns = [
            r'\*\*Step\s*(\d+)[:\s]*([^\*]+)\*\*\s*\((\d+)\s*(?:min|minutes)?\)',
            r'Step\s*(\d+)[:\s]*\*\*([^\*]+)\*\*\s*\((\d+)\s*(?:min|minutes)?\)',
            r'###?\s*Step\s*(\d+)[:\s]*([^\n]+?)\s*\((\d+)\s*(?:min|minutes)?\)',
        ]
        
        for pattern in step_patterns:
            step_matches = re.findall(pattern, text, re.IGNORECASE)
            if step_matches:
                for step_num, step_title, duration in step_matches[:5]:
                    result["recovery_steps"].append(
                        PlaybookAction(
                            step_number=int(step_num),
                            action=step_title.strip(),
                            duration_minutes=int(duration),
                        )
                    )
                break
        
        # If no steps parsed, try simpler format with bold titles
        if not result["recovery_steps"]:
            simple_steps = re.findall(r'\*\*Step\s*(\d+)[^:]*:\s*([^\*\n]+)', text, re.IGNORECASE)
            for step_num, step_title in simple_steps[:5]:
                result["recovery_steps"].append(
                    PlaybookAction(
                        step_number=int(step_num),
                        action=step_title.strip(),
                        duration_minutes=3,
                    )
                )
        
        # Try Recovery Steps section with numbered items
        if not result["recovery_steps"]:
            recovery_match = re.search(r'Recovery Steps[^\n]*\n((?:[\d]+[\.:\)].+\n?)+)', text, re.IGNORECASE)
            if recovery_match:
                items = re.findall(r'[\d]+[\.:\)]\s*(.+?)(?:\n|$)', recovery_match.group(1))
                for i, item in enumerate(items[:5], 1):
                    result["recovery_steps"].append(
                        PlaybookAction(
                            step_number=i,
                            action=item.strip(),
                            duration_minutes=3,
                        )
                    )
        # Generate YouTube search links based on detected topic
        # AI cannot generate real YouTube URLs - generate search links instead
        subject = result.get("subject", "")
        topic = result.get("topic", "")
        title = result.get("title", "")
        
        # Build search query from available context
        search_query = ""
        if topic:
            search_query = topic
        elif title and len(title) > 10:
            search_query = title
        else:
            # Extract topic from title/summary
            search_query = re.sub(r'[^\w\s]', '', result.get("summary", "")[:50])
        
        if search_query:
            import urllib.parse
            encoded_query = urllib.parse.quote(f"{search_query} {subject} class".strip())
            
            # Add relevant YouTube search links
            result["youtube_videos"] = [
                VideoResource(
                    title=f"📚 {search_query} - Educational Video",
                    url=f"https://www.youtube.com/results?search_query={encoded_query}+NCERT+Hindi",
                    description="Search for Hindi medium educational videos"
                ),
                VideoResource(
                    title=f"🎓 {search_query} - Khan Academy Style",
                    url=f"https://www.youtube.com/results?search_query={encoded_query}+Khan+Academy+India",
                    description="Search for Khan Academy India videos"
                ),
                VideoResource(
                    title=f"📖 {search_query} - BYJU'S / Vedantu",
                    url=f"https://www.youtube.com/results?search_query={encoded_query}+BYJU+Vedantu",
                    description="Search for BYJU'S and Vedantu explanations"
                ),
            ]
        
        print(f"YouTube: generated {len(result['youtube_videos'])} search links for '{search_query}'")
        
        # Extract NCERT Reference - more flexible pattern
        ncert_patterns = [
            r'###?\s*NCERT Reference[^\n]*\n(.*?)(?=###|\n\n|$)',
            r'NCERT Reference[:\s]*(.*?)(?=###|\n\n|$)',
            r'\*\*Chapter\*\*[:\s]*([^\n]+)',
        ]
        for pattern in ncert_patterns:
            ncert_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if ncert_match:
                ncert_text = ncert_match.group(1).strip()[:500]
                if ncert_text and len(ncert_text) > 10:
                    result["ncert_reference"] = ncert_text
                    break
        
        # Extract Teaching Tips - more flexible patterns
        tips_with_emoji = re.findall(r'[💡🔹•]\s*(.+?)(?:\n|$)', text)
        tips_section = re.search(r'(?:Quick )?Teaching Tips[^\n]*\n(.*?)(?=###|\n\n|$)', text, re.IGNORECASE | re.DOTALL)
        
        if tips_with_emoji:
            result["teaching_tips"] = [t.strip() for t in tips_with_emoji[:5] if t.strip() and len(t.strip()) > 5]
        elif tips_section:
            tips = re.findall(r'[-•*]\s*(.+?)(?:\n|$)', tips_section.group(1))
            result["teaching_tips"] = [t.strip() for t in tips[:5] if t.strip() and len(t.strip()) > 5]
        
        # Add generic helpful tips if none found
        if not result["teaching_tips"]:
            result["teaching_tips"] = [
                "Use visual aids like diagrams and charts",
                "Break complex concepts into smaller steps", 
                "Encourage peer discussion and teaching",
                "Relate topics to real-world examples students know",
                "Check understanding with quick formative questions"
            ]
        
        # Extract Teaching Resources
        resources_section = re.search(r'Teaching Resources[^\n]*\n(.*?)(?=###|\n\n|$)', text, re.IGNORECASE | re.DOTALL)
        if resources_section:
            resource_patterns = [
                r'\*\*([^*]+)\*\*[:\s]*(.+?)(?:\n|$)',
                r'\d+\.\s*\*\*([^*]+)\*\*[:\s]*(.+?)(?:\n|$)',
            ]
            for pattern in resource_patterns:
                resource_lines = re.findall(pattern, resources_section.group(1))
                if resource_lines:
                    for resource_type, desc in resource_lines[:5]:
                        result["teaching_resources"].append(
                            TeachingResource(
                                title=desc.strip()[:200],
                                url="",
                                resource_type=resource_type.strip().lower(),
                                description=desc.strip()[:200],
                            )
                        )
                    break
        
        # Add default teaching resources if none found
        if not result["teaching_resources"]:
            result["teaching_resources"] = [
                TeachingResource(
                    title="DIKSHA App - Free NCERT Content",
                    url="https://diksha.gov.in/",
                    resource_type="diksha",
                    description="Official government e-learning platform"
                ),
                TeachingResource(
                    title="NCERT Textbooks Online",
                    url="https://ncert.nic.in/textbook.php",
                    resource_type="ncert",
                    description="Free downloadable NCERT textbooks"
                ),
            ]
        
        print(f"Parsed: title='{result['title'][:30]}...', {len(result['immediate_actions'])} actions, {len(result['youtube_videos'])} videos, {len(result['teaching_tips'])} tips")
        
        return result
    
    async def _update_memory(self, sos_request: SOSRequest):
        """
        Update classroom memory with this SOS request.
        
        This helps build patterns over time for better recommendations.
        """
        try:
            # Get or create memory for this teacher
            memory = await ClassroomMemory.find_one(
                ClassroomMemory.teacher_id == sos_request.teacher_id
            )
            
            if not memory:
                memory = ClassroomMemory(teacher_id=sos_request.teacher_id)
            
            # Record this SOS
            memory.record_sos(
                subject=sos_request.subject,
                issue_type=sos_request.context_type.value if sos_request.context_type else None
            )
            
            await memory.save()
            
        except Exception as e:
            # Don't fail the main request if memory update fails
            print(f"Warning: Failed to update memory: {e}")
    
    async def get_teacher_stats(self, teacher_id: str) -> Dict[str, Any]:
        """
        Get statistics for a teacher's dashboard.
        """
        memory = await ClassroomMemory.find_one(
            ClassroomMemory.teacher_id == teacher_id
        )
        
        if not memory:
            return {
                "total_sos_requests": 0,
                "total_successful_resolutions": 0,
                "top_issues": [],
                "best_strategies": [],
                "subjects_taught": [],
            }
        
        return {
            "total_sos_requests": memory.total_sos_requests,
            "total_successful_resolutions": memory.total_successful_resolutions,
            "top_issues": [
                {"issue": p.issue_type, "count": p.occurrence_count}
                for p in memory.get_top_issues(5)
            ],
            "best_strategies": [
                {"summary": s.strategy_summary, "rating": s.effectiveness_rating}
                for s in memory.get_best_strategies(5)
            ],
            "subjects_taught": memory.subjects_taught,
        }


# Singleton instance
pedagogy_engine = PedagogyEngine()
