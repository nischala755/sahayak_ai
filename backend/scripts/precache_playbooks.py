"""
SAHAYAK AI - Offline Playbook Pre-caching Script
=================================================

This script pre-caches the 50 most common classroom scenarios
for offline use in rural areas with intermittent internet.

Run with: python scripts/precache_playbooks.py
"""

import asyncio
import aiohttp
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Most common teaching scenarios for Indian government schools
COMMON_SCENARIOS = [
    # Mathematics
    ("Mathematics", "1", "Students can't recognize numbers 1-10"),
    ("Mathematics", "2", "Students struggling with addition of single digits"),
    ("Mathematics", "3", "Students not understanding multiplication tables"),
    ("Mathematics", "4", "Students confused about fractions"),
    ("Mathematics", "5", "Students can't understand decimals"),
    ("Mathematics", "6", "Students struggling with algebra basics"),
    ("Mathematics", "7", "Students confused about integers"),
    ("Mathematics", "8", "Students don't understand geometry theorems"),
    
    # Science
    ("Science", "3", "Students don't understand living vs non-living things"),
    ("Science", "4", "Students confused about states of matter"),
    ("Science", "5", "Students can't understand the solar system"),
    ("Science", "6", "Students struggling with photosynthesis"),
    ("Science", "7", "Students don't understand chemical reactions"),
    ("Science", "8", "Students confused about human body systems"),
    
    # English
    ("English", "1", "Students can't recognize alphabets"),
    ("English", "2", "Students struggling with reading simple words"),
    ("English", "3", "Students can't form simple sentences"),
    ("English", "4", "Students confused about tenses"),
    ("English", "5", "Students struggling with comprehension passages"),
    ("English", "6", "Students can't write paragraphs properly"),
    
    # Hindi
    ("Hindi", "1", "Students can't recognize Hindi varnamala"),
    ("Hindi", "2", "Students struggling with matra"),
    ("Hindi", "3", "Students confused about sandhi"),
    ("Hindi", "4", "Students can't write Hindi sentences"),
    ("Hindi", "5", "Students struggling with Hindi grammar"),
    
    # Social Studies
    ("Social Studies", "4", "Students confused about maps and directions"),
    ("Social Studies", "5", "Students don't understand Indian history"),
    ("Social Studies", "6", "Students confused about Indian geography"),
    ("Social Studies", "7", "Students struggling with civics concepts"),
    ("Social Studies", "8", "Students don't understand economics basics"),
    
    # EVS (Environmental Studies)
    ("EVS", "3", "Students don't understand plants and animals"),
    ("EVS", "4", "Students confused about weather and seasons"),
    ("EVS", "5", "Students struggling with pollution and environment"),
    
    # Common Classroom Management
    ("General", "any", "Students are not paying attention in class"),
    ("General", "any", "Students are too noisy and disruptive"),
    ("General", "any", "Some students are very shy and don't participate"),
    ("General", "any", "Students are tired and sleepy after lunch"),
    ("General", "any", "Students have mixed learning levels in class"),
    ("General", "any", "Students forget what was taught yesterday"),
    ("General", "any", "Students are not doing homework"),
    ("General", "any", "Students are copying from each other"),
    ("General", "any", "Parents are not supportive of education"),
    ("General", "any", "Students have language barrier issues"),
    ("General", "any", "Too many students in one classroom"),
    ("General", "any", "No teaching materials available"),
    ("General", "any", "Students are afraid to ask questions"),
    ("General", "any", "Students learn at very different speeds"),
    ("General", "any", "First generation learners struggling"),
]

API_BASE = "http://localhost:8000/api/v1"

async def precache_playbook(session: aiohttp.ClientSession, subject: str, grade: str, problem: str):
    """Pre-cache a single playbook scenario."""
    try:
        # Build query
        query = f"{problem}"
        params = {
            "raw_input": query,
            "subject": subject if subject != "General" else None,
            "grade": grade if grade != "any" else None,
        }
        # Filter out None values
        params = {k: v for k, v in params.items() if v is not None}
        
        async with session.post(f"{API_BASE}/sos/quick", params=params) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("from_cache"):
                    return "cached"
                else:
                    return "new"
            else:
                return f"error:{response.status}"
    except Exception as e:
        return f"error:{str(e)[:30]}"

async def main():
    """Pre-cache all common scenarios."""
    print("=" * 60)
    print("SAHAYAK AI - Offline Playbook Pre-caching")
    print("=" * 60)
    print(f"Pre-caching {len(COMMON_SCENARIOS)} common scenarios...")
    print()
    
    # Stats
    cached = 0
    new = 0
    errors = 0
    
    async with aiohttp.ClientSession() as session:
        for i, (subject, grade, problem) in enumerate(COMMON_SCENARIOS, 1):
            result = await precache_playbook(session, subject, grade, problem)
            
            status_icon = "✅" if result in ("cached", "new") else "❌"
            cache_icon = "⚡" if result == "cached" else "🆕" if result == "new" else "⚠️"
            
            print(f"[{i:2d}/{len(COMMON_SCENARIOS)}] {status_icon} {subject:15} Grade {grade:3} | {cache_icon}")
            
            if result == "cached":
                cached += 1
            elif result == "new":
                new += 1
            else:
                errors += 1
                print(f"         Error: {result}")
            
            # Small delay to avoid overwhelming the API
            await asyncio.sleep(0.5)
    
    print()
    print("=" * 60)
    print("Pre-caching Complete!")
    print("=" * 60)
    print(f"  New playbooks generated: {new}")
    print(f"  Already cached:          {cached}")
    print(f"  Errors:                  {errors}")
    print(f"  Total cached:            {new + cached}")
    print()
    print("Playbooks will remain cached for 24 hours.")
    print("Teachers can now use SAHAYAK AI offline!")

if __name__ == "__main__":
    asyncio.run(main())
