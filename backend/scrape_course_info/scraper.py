import asyncio
import json
import random
from pydantic import BaseModel, Field
from typing import Optional, List
import os
from playwright.async_api import async_playwright, TimeoutError

# 1. The Schema
class Course(BaseModel):
    title: str = Field(...)
    provider: str = Field(default="Coursera")
    url: str = Field(default="")
    thumbnail_url: Optional[str] = Field(default="", description="URL for the course image") # <-- ADD THIS!
    partner_institution: Optional[str] = Field(None)
    category: Optional[str] = Field(None)
    raw_data: List[str] = Field(default_factory=list)

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

async def bulk_scrape_coursera():
    # Use a dictionary to prevent duplicate courses (using title as the unique key)
    unique_courses = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False, # Keep false to watch it work, change to True if you want it hidden
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print(f"Starting bulk scrape for {len(KEYWORDS)} keywords...")

        for index, query in enumerate(KEYWORDS):
            print(f"\n[{index + 1}/{len(KEYWORDS)}] Searching for: '{query}'")
            search_url = f"https://www.coursera.org/search?query={query.replace(' ', '%20')}"
            
            try:
                await page.goto(search_url, wait_until="domcontentloaded")
                target_selector = '.cds-ProductCard-base' 
                await page.wait_for_selector(target_selector, timeout=15000)
                
                courses_elements = await page.query_selector_all(target_selector)
                added_this_round = 0
                
                for element in courses_elements:
                    raw_text = await element.inner_text()
                    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
                    
                    if len(lines) < 2:
                        continue 
                    
                    partner = lines[0]
                    title = lines[1]
                    
                    category_value = None
                    for line in lines:
                        if line.startswith("Category:"):
                            category_value = line.replace("Category:", "").strip()
                            break

                    link_element = await element.query_selector('a')
                    url_path = await link_element.get_attribute('href') if link_element else ""
                    full_url = f"https://www.coursera.org{url_path}" if url_path.startswith('/') else url_path
                    img_element = await element.query_selector('img')
                    thumbnail_url = await img_element.get_attribute('src') if img_element else ""
                    
                    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
                            
                    # Duplicate check: Only add if we haven't seen this title yet
                    if title not in unique_courses:
                        course_obj = Course(
                            title=title,
                            provider="Coursera",
                            url=full_url,
                            thumbnail_url=thumbnail_url, # <-- ADD IT HERE
                            partner_institution=partner,
                            category=category_value,
                            raw_data=lines
                        )
                        unique_courses[title] = course_obj.model_dump()
                        added_this_round += 1
                    
                
                print(f"Found {added_this_round} new unique courses.")
 
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(list(unique_courses.values()), f, indent=4, ensure_ascii=False)
                
                # BOT PROTECTION: Wait a random amount of time (2 to 5 seconds) before the next search
                delay = random.uniform(2.0, 5.0)
                print(f"Waiting {delay:.1f} seconds to avoid bot detection...")
                await asyncio.sleep(delay)
                
            except TimeoutError:
                print(f"Timeout on '{query}'. Skipping to next keyword...")
                continue # Skip this keyword and keep going
                
        print(f"\Scrape Complete! Total unique courses saved: {len(unique_courses)}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(bulk_scrape_coursera())