import re
import asyncio
import json
import random
import os
from pydantic import BaseModel, Field
from typing import Optional, List
from playwright.async_api import async_playwright, TimeoutError

# 1. The Schema
class Course(BaseModel):
    title: str = Field(...)
    provider: str = Field(default="Coursera")
    url: str = Field(default="")
    thumbnail_url: Optional[str] = Field(default="")
    partner_institution: Optional[str] = Field(None)
    category: Optional[str] = Field(None)
    raw_data: List[str] = Field(default_factory=list)
    duration_minutes: Optional[int] = 0 
    match_score: Optional[int] = 0

# 2. Keywords
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

# --- HELPER: Metadata Logic ---
def extract_clean_metadata(lines: List[str]):
    """
    Sifts through the raw text lines to find the actual Partner and Title,
    ignoring 'New' badges, 'Credit' labels, and single-letter logo alts.
    """
    noise_labels = {"new", "credit offered", "professional certificate", "specialization", "course", "guided project", "degree"}
    
    # Filter out empty strings, single characters (like 'G'), and UI noise
    filtered = [
        line for line in lines 
        if len(line.strip()) > 1 and line.strip().lower() not in noise_labels
    ]
    
    partner = "Coursera Partner"
    title = "Unknown Course"
    
    if len(filtered) >= 2:
        # In the new logic, [0] is the Partner (Google) and [1] is the Title (Google AI)
        partner = filtered[0]
        title = filtered[1]
    elif len(filtered) == 1:
        title = filtered[0]
        
    return title, partner

# --- MAIN SCRAPER ---
async def bulk_scrape_coursera():
    unique_courses = {}
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.abspath(os.path.join(script_dir, ".."))
    output_path = os.path.join(backend_dir, 'courses.json') # Standardized filename

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print(f"🚀 Starting robust scrape for {len(KEYWORDS)} keywords...")

        for index, query in enumerate(KEYWORDS):
            print(f"\n[{index + 1}/{len(KEYWORDS)}] Searching: '{query}'")
            search_url = f"https://www.coursera.org/search?query={query.replace(' ', '%20')}"
            
            try:
                await page.goto(search_url, wait_until="domcontentloaded")
                target_selector = '.cds-ProductCard-base' 
                await page.wait_for_selector(target_selector, timeout=10000)
                
                elements = await page.query_selector_all(target_selector)
                added_count = 0
                
                for el in elements:
                    raw_text = await el.inner_text()
                    lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
                    
                    if len(lines) < 1: continue

                    # 1. CLEAN METADATA (The Fix!)
                    title, partner = extract_clean_metadata(lines)

                    # 2. CATEGORY
                    category_val = "Course"
                    for l in lines:
                        if l.startswith("Category:"):
                            category_val = l.replace("Category:", "").strip()
                    
                    # 3. URL & IMAGE
                    link_el = await el.query_selector('a')
                    path = await link_el.get_attribute('href') if link_el else ""
                    full_url = f"https://www.coursera.org{path}" if path.startswith('/') else path
                    
                    img_el = await el.query_selector('img')
                    thumb = await img_el.get_attribute('src') if img_el else ""

                    # 4. DURATION (Keeping your existing logic)
                    duration = 120
                    card_lower = raw_text.lower()
                    hour_match = re.search(r'(\d+)\s*(?:hour|hr|hrs)', card_lower)
                    commitment_match = re.search(r'(\d+)\s*week.*?(\d+)\s*hour', card_lower)
                    
                    if commitment_match:
                        duration = int(commitment_match.group(1)) * int(commitment_match.group(2)) * 60
                    elif hour_match:
                        duration = int(hour_match.group(1)) * 60
                    elif "month" in card_lower:
                        duration = 1800 

                    # 5. SAVE UNIQUE
                    if title not in unique_courses:
                        course_obj = Course(
                            title=title,
                            provider="Coursera",
                            url=full_url,
                            thumbnail_url=thumb,
                            partner_institution=partner,
                            category=category_val,
                            duration_minutes=duration,
                            raw_data=lines
                        )
                        unique_courses[title] = course_obj.model_dump()
                        added_count += 1
                
                print(f"   ✅ Added {added_count} new courses.")

                # Continuous Saving
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(list(unique_courses.values()), f, indent=4, ensure_ascii=False)
                
                await asyncio.sleep(random.uniform(1.5, 3.5))
                
            except Exception as e:
                print(f"   ⚠️ Skipping '{query}' due to error.")
                continue
                
        await browser.close()
        print(f"\n🎉 Done! Total courses: {len(unique_courses)}")

if __name__ == "__main__":
    async_run = asyncio.run(bulk_scrape_coursera())