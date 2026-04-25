from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import json
import os

# THIS is the "app" Uvicorn was looking for!
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_courses():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    coursera_path = os.path.join(base_dir, "courses.json")
    youtube_path = os.path.join(base_dir, "youtube_courses.json")
    
    all_courses = []
    
    if os.path.exists(coursera_path):
        with open(coursera_path, "r", encoding="utf-8") as f:
            coursera_data = json.load(f)
            all_courses.extend(coursera_data)
            print(f"✅ Loaded {len(coursera_data)} Coursera courses.")
            
    if os.path.exists(youtube_path):
        with open(youtube_path, "r", encoding="utf-8") as f:
            youtube_data = json.load(f)
            all_courses.extend(youtube_data)
            print(f"✅ Loaded {len(youtube_data)} YouTube courses.")
            
    print(f"🚀 Total database size: {len(all_courses)} courses ready for search.\n")
    return all_courses

# Load the database into memory
DATABASE = load_courses()

@app.get("/api/search")
def search_courses(q: str = Query("", description="The search term")):
    query = q.lower()
    
    if not query:
        return DATABASE 
        
    results = []
    for course in DATABASE:
        title = course.get("title", "").lower()
        partner = course.get("partner_institution", "").lower()
        category = course.get("category", "").lower()
        
        if query in title or query in partner or query in category:
            results.append(course)
            
    return results