import asyncio
import httpx
import json
import os
from pydantic import BaseModel, Field
from typing import Optional, List
from dotenv import load_dotenv


# 1. The Exact Same Schema
class Course(BaseModel):
    title: str = Field(..., description="The main title of the course")
    provider: str = Field(default="YouTube", description="The platform hosting it")
    url: str = Field(default="", description="The direct link to the course")
    partner_institution: Optional[str] = Field(None, description="The Channel Name")
    category: Optional[str] = Field(None, description="E.g., 'Free Video Course'")
    raw_data: List[str] = Field(default_factory=list)

load_dotenv()

# Now you can safely fetch the key
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

if not YOUTUBE_API_KEY:
    print("Warning: API key not found. Check your .env file.")
else:
    print("API key loaded successfully!")

# 2. The 30 Keywords
KEYWORDS = [
    "python programming", "data structures algorithms", "machine learning", "artificial intelligence", 
    "web development full stack", "react.js front end", "node.js backend", "cloud computing aws", 
    "sql database design", "mobile app development", "cybersecurity basics", "ethical hacking", 
    "network security", "penetration testing", "cryptography", "information security management", 
    "incident response", "malware analysis", "cloud security", "comptia security+", 
    "product management", "project management pmp", "digital marketing", "financial analysis", 
    "entrepreneurship startup", "business analytics", "leadership and management", 
    "supply chain logistics", "corporate finance", "agile scrum master"
]

script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(script_dir, ".."))
output_path = os.path.join(backend_dir, 'courses.json')

async def bulk_fetch_youtube():
    unique_youtube_courses = {}
    url = "https://www.googleapis.com/youtube/v3/search"
    
    print(f"Starting YouTube bulk fetch for {len(KEYWORDS)} keywords...")

    async with httpx.AsyncClient() as client:
        for index, query in enumerate(KEYWORDS):
            print(f"\n[{index + 1}/{len(KEYWORDS)}] Fetching YouTube data for: '{query}'")
            
            params = {
                "part": "snippet",
                "q": f"{query} full course",
                "type": "video",
                # "videoDuration": "long",  <-- Commenting this out usually fixes the empty list issue!
                "maxResults": 10,
                "key": YOUTUBE_API_KEY
            }
            
            try:
                response = await client.get(url, params=params)
                
                # Added response.text here so if it DOES error, we see the exact reason
                if response.status_code != 200:
                    print(f"⚠️ API Error on '{query}': {response.status_code} - {response.text}")
                    continue
                    
                data = response.json()
                
                # --- NEW DEBUG BLOCK ---
                # This will print the raw data for the very first keyword so we can inspect it
                if index == 0:
                    print("\n--- RAW YOUTUBE API RESPONSE ---")
                    # We only print the top-level keys to not flood your terminal
                    print(f"Keys in response: {list(data.keys())}")
                    print(f"Number of items found: {len(data.get('items', []))}")
                    print("--------------------------------\n")
                # -----------------------
                
                for item in data.get("items", []):
                    video_id = item["id"]["videoId"]
                    title = item["snippet"]["title"]
                    channel_name = item["snippet"]["channelTitle"]
                    description = item["snippet"]["description"]
                    
                    # --- ADD THIS LINE ---
                    thumbnail = item["snippet"]["thumbnails"]["high"]["url"]
                    
                    if title not in unique_youtube_courses:
                        course_obj = Course(
                            title=title,
                            provider="YouTube",
                            url=f"https://www.youtube.com/watch?v={video_id}",
                            thumbnail_url=thumbnail, # <-- ADD IT HERE
                            partner_institution=channel_name,
                            category="Free Video Course",
                            raw_data=[description]
                        )
                        
                print(f"✅ Found {added_this_round} new unique YouTube courses.")
                
                # Save progress after every keyword
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(list(unique_youtube_courses.values()), f, indent=4, ensure_ascii=False)
                    
            except Exception as e:
                print(f"⚠️ Failed to fetch '{query}': {e}")
                
            # A small delay to respect API rate limits (even though it's much faster than Playwright)
            await asyncio.sleep(1.0)
            
    print(f"\n🎉 YouTube Fetch Complete! Total unique courses saved: {len(unique_youtube_courses)}")

if __name__ == "__main__":
    asyncio.run(bulk_fetch_youtube())