"""
============================================
SAHAYAK AI - Gemini AI Service
============================================

Wrapper for Google Gemini AI API. Handles all communication
with the AI model for generating teaching playbooks.
============================================
"""

import asyncio
import google.generativeai as genai
from typing import Optional, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings


class GeminiService:
    """
    Service for interacting with Google Gemini AI.
    
    Handles all AI model calls with proper error handling,
    retry logic, and response parsing.
    """
    
    def __init__(self):
        """Initialize the Gemini client."""
        self.api_key = settings.gemini_api_key
        self._configured = False
        self.model = None
        
        if self.api_key and self.api_key != "your-gemini-api-key-here":
            self._configure()
    
    def _configure(self):
        """Configure the Gemini API client."""
        try:
            genai.configure(api_key=self.api_key)
            
            # Use Gemini 2.5 Flash model (latest, fast and capable)
            self.model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40,
                    "max_output_tokens": 2048,
                }
            )
            
            self._configured = True
            print("✅ Gemini AI configured successfully with gemini-2.5-flash model")
        except Exception as e:
            print(f"❌ Gemini configuration failed: {e}")
            self._configured = False
    
    def is_available(self) -> bool:
        """Check if Gemini AI is available."""
        return self._configured and self.model is not None
    
    async def generate_response(
        self,
        prompt: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a response from Gemini AI.
        
        Uses asyncio.to_thread to run the synchronous Gemini API
        call in a thread pool, preventing blocking.
        """
        if not self.is_available():
            print("Gemini AI not available - using fallback")
            return {
                "success": False,
                "error": "Gemini AI not configured. Please set GEMINI_API_KEY.",
                "text": self._get_fallback_response(prompt)
            }
        
        try:
            # Combine context and prompt
            full_prompt = prompt
            if context:
                full_prompt = f"Context: {context}\n\n{prompt}"
            
            # Run synchronous Gemini call in thread pool
            # This is the correct way to use sync APIs in async code
            response = await asyncio.to_thread(
                self.model.generate_content,
                full_prompt
            )
            
            # Extract response text
            if response and response.text:
                print(f"Gemini response received: {len(response.text)} chars")
                return {
                    "success": True,
                    "text": response.text,
                    "prompt_tokens": getattr(response, 'prompt_token_count', None),
                    "response_tokens": getattr(response, 'candidates_token_count', None),
                }
            else:
                print("Gemini returned empty response")
                return {
                    "success": False,
                    "error": "Empty response from Gemini",
                    "text": self._get_fallback_response(prompt)
                }
            
        except Exception as e:
            print(f"Gemini API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": self._get_fallback_response(prompt)
            }
    
    def _get_fallback_response(self, prompt: str) -> str:
        """
        Provide a fallback response when AI is unavailable.
        """
        return """
## Teaching Rescue Playbook

### Title
Classroom Recovery Strategy

### Summary
This is a generic fallback playbook. For personalized AI-generated strategies, please ensure your Gemini API key is properly configured.

### Immediate Actions (Do RIGHT NOW - 30 seconds)
1. Take a deep breath and pause the current activity
2. Get students' attention using a signal (clap pattern, bell)
3. Acknowledge the challenge: "I can see some of us are finding this tricky"

### Recovery Steps (Next 10-15 minutes)
**Step 1: Step Back** (3 minutes)
- What to do: Revisit the prerequisite concept briefly
- What to say: "Let's take a quick step back and review what we learned before"
- Expected outcome: Students recall prior knowledge

**Step 2: Concrete Example** (4 minutes)
- What to do: Use a real-world example students can relate to
- What to say: "Let me show you how this works in everyday life"
- Expected outcome: Students connect abstract concept to reality

**Step 3: Peer Support** (5 minutes)
- What to do: Pair students who understand with those who need help
- What to say: "Turn to your partner and explain what you understood"
- Expected outcome: Peer teaching reinforces learning

### Alternative Strategies
1. Try a visual representation (drawing, diagram)
2. Use manipulatives if available
3. Break the problem into smaller steps

### Success Indicators
- Students asking clarifying questions (shows engagement)
- At least 60% can explain the concept to a partner
- Reduced confusion visible on faces

### Time Estimate: 15 minutes
### Difficulty: Medium

*Note: This is a generic fallback playbook. Configure your Gemini API key for personalized AI-generated strategies.*
"""
    
    async def generate_playbook(
        self,
        problem_description: str,
        classroom_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a teaching playbook for a classroom problem.
        """
        # Build the pedagogical prompt
        prompt = self._build_pedagogy_prompt(problem_description, classroom_context)
        
        print(f"Generating playbook for: {problem_description[:50]}...")
        
        # Get AI response
        response = await self.generate_response(prompt)
        
        return response
    
    def _build_pedagogy_prompt(
        self,
        problem: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Build a structured prompt for pedagogical assistance.
        """
        subject = context.get("subject", "General")
        grade = context.get("grade", "Unknown")
        topic = context.get("topic", "Unknown")
        student_count = context.get("student_count", "30")
        urgency = context.get("urgency", "medium")
        language = context.get("language", "English")
        
        prompt = f"""You are SAHAYAK AI, an expert pedagogy coach for government school teachers in India.

## TEACHER'S EMERGENCY REQUEST
"{problem}"

## CLASSROOM CONTEXT
- Subject: {subject}
- Grade/Class: {grade}
- Topic: {topic}
- Number of Students: {student_count}
- Urgency Level: {urgency}
- Language Preference: {language}

## YOUR TASK
Generate an immediate teaching rescue playbook with helpful resources. The teacher needs help RIGHT NOW.

## OUTPUT FORMAT (Use this exact structure with markdown):

### Title
[Brief title for this rescue strategy - specific to the problem]

### Summary
[One paragraph summary of the approach tailored to this specific classroom situation]

### Immediate Actions (Do RIGHT NOW - 30 seconds)
1. [First immediate action]
2. [Second immediate action]
3. [Third immediate action]

### Recovery Steps (Next 10-15 minutes)
**Step 1: [Step Title]** (X minutes)
- What to do: [Detailed instruction]
- What to say: "[Exact teacher dialogue]"
- Expected outcome: [What should happen]

**Step 2: [Step Title]** (X minutes)
- What to do: [Detailed instruction]
- What to say: "[Exact teacher dialogue]"
- Expected outcome: [What should happen]

**Step 3: [Step Title]** (X minutes)
- What to do: [Detailed instruction]
- What to say: "[Exact teacher dialogue]"
- Expected outcome: [What should happen]

### Alternative Strategies
If the main approach doesn't work:
1. [Alternative 1 - specific to this problem]
2. [Alternative 2 - creative approach]

### Success Indicators
How to know if the strategy is working:
- [Indicator 1]
- [Indicator 2]
- [Indicator 3]

### YouTube Videos (Recommended for this topic)
Provide 2-3 relevant educational YouTube videos that the teacher can show students or use for reference:
1. **[Video Title]** - https://youtube.com/watch?v=[video_id] - [Brief description, 5-10 min]
2. **[Video Title]** - https://youtube.com/watch?v=[video_id] - [Brief description]
3. **[Video Title]** - https://youtube.com/watch?v=[video_id] - [Brief description]

(Use real, popular educational YouTube channels like: Khan Academy India, BYJU'S, Vedantu, Unacademy, NCERT Official, Diksha, LearnVern, etc.)

### NCERT Reference
- **Chapter**: [NCERT Book Name, Class X, Chapter Y - Chapter Name]
- **Page Numbers**: [Relevant page numbers]
- **Key Concepts**: [Concepts covered in this section]

### Teaching Resources
1. **DIKSHA App**: [Specific module or lesson name]
2. **NCERT Textbook**: [Chapter and section reference]
3. **Online Resource**: [Any free educational website]

### Quick Teaching Tips
- 💡 [Tip 1 - specific to this topic]
- 💡 [Tip 2 - classroom management tip]
- 💡 [Tip 3 - engagement tip]

### Time Estimate: [X] minutes
### Difficulty: [Easy/Medium/Hard]

## IMPORTANT GUIDELINES
- Be SPECIFIC to the actual problem described
- Only use materials typically available in government schools
- Instructions must be doable by a single teacher
- Strategies should work for large class sizes (30-50 students)
- Use culturally appropriate examples for Indian context
- Keep language simple and actionable
- DO NOT give generic advice - tailor everything to this specific situation
- For YouTube videos, suggest REAL educational channels popular in India
- NCERT references should be accurate for the grade level

## LANGUAGE INSTRUCTION (CRITICAL):
Generate the ENTIRE playbook in **{language}** language.
- If language is "Hindi": Write everything in Hindi (Devanagari script). Use हिंदी for all content.
- If language is "Kannada": Write everything in Kannada (ಕನ್ನಡ script). Use ಕನ್ನಡ for all content.
- If language is "English": Write in simple English suitable for government school teachers.
Keep markdown headers in English for parsing, but ALL content (title, summary, actions, tips) MUST be in the requested language.
"""
        
        return prompt


# Singleton instance
gemini_service = GeminiService()
