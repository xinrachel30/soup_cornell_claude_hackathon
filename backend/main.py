from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 1. UPDATED MODELS ---
# We add the new fields so FastAPI doesn't "strip" them out before sending to React
class Course(BaseModel):
    title: str
    provider: str
    url: str
    thumbnail_url: Optional[str] = ""
    partner_institution: Optional[str] = None
    category: Optional[str] = None
    duration_minutes: Optional[int] = 0
    match_score: Optional[float] = 0
    # Added for Gemini insights:
    vibe_summary: Optional[str] = None
    reasoning: Optional[str] = None
    features: Optional[Dict[str, Any]] = None
    scores: Optional[Dict[str, Any]] = None
    featured_review: Optional[Dict[str, Any]] = None

def load_db():
    raw_db = []
    enriched_data = {}
    
    # 🔎 Step A: Load the raw lists
    target_files = ['courses.json', 'youtube_courses.json']
    search_dirs = [".", "./scrape_course_info"]

    for filename in target_files:
        for directory in search_dirs:
            full_path = os.path.join(directory, filename)
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    raw_db.extend(json.load(f))
                break

    # 💎 Step B: Load the "Gold" data (scored_courses.json)
    # This file is a DICTIONARY keyed by Title
    scored_path = ""
    for directory in search_dirs:
        temp_path = os.path.join(directory, 'scored_courses.json')
        if os.path.exists(temp_path):
            scored_path = temp_path
            break

    if scored_path:
        with open(scored_path, 'r', encoding='utf-8') as f:
            enriched_data = json.load(f)
            print(f"✅ Loaded enriched data for {len(enriched_data)} courses.")

    # 🤝 Step C: The "Smart Join"
    # We loop through the raw list and "patch" in the Gemini insights
    final_db = []
    for course in raw_db:
        title = course.get("title")
        # If this title exists in our Gemini-scored dictionary, merge it!
        if title in enriched_data:
            course.update(enriched_data[title])
        
        final_db.append(course)

    print(f"📦 Final Database: {len(final_db)} courses ready.")
    return final_db

DATABASE = load_db()

@app.get("/api/recommend")
def recommend_courses(
    q: str = Query("", description="Search query"), 
    budget: str = Query("any"), 
    time: str = Query("any")
):
    # (Your existing TIME_MAP and filtering logic remains the same...)
    TIME_MAP = {
        "snack": (1, 45),
        "weekend": (46, 300),
        "cert": (301, 2400),
        "mastery": (2401, 999999),
        "any": (0, 999999)
    }
    
    target_min, target_max = TIME_MAP.get(time, (0, 999999))
    query = q.lower().strip()
    scored_results = []

    for course in DATABASE:
        title = course.get("title", "").lower()
        category = course.get("category", "").lower()
        
        if query and (query not in title and query not in category):
            continue
            
        score = 10 
        
        # Duration logic
        try:
            dur = int(course.get("duration_minutes", 0))
        except:
            dur = 0
            
        if dur > 0:
            if target_min <= dur <= target_max:
                score += 80 
            elif time != "any":
                score -= 50 
        else:
            score += 20 
        
        # Provider logic
        provider = course.get("provider", "")
        if budget == "free" and provider == "YouTube":
            score += 30
        elif budget == "paid" and provider == "Coursera":
            score += 30

        course_copy = course.copy()
        course_copy["match_score"] = score
        scored_results.append(course_copy)

    return sorted(scored_results, key=lambda x: x.get("match_score", 0), reverse=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)