import time
import json
import os
from google import genai
from google.api_core import exceptions # Need this for 429 handling
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Use 2.5 Flash for the higher free-tier quota
MODEL_ID = "gemini-2.5-flash" 

def analyze_with_retry(course_title, reviews, retries=3):
    """Wraps the API call to handle 429 errors gracefully."""
    context = "\n".join(reviews)
    prompt = f"Analyze these reviews for '{course_title}': {context}..." # (Your full prompt here)
    
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=prompt,
                config={'response_mime_type': 'application/json'}
            )
            return json.loads(response.text)
        
        except exceptions.ResourceExhausted as e:
            wait_time = (attempt + 1) * 30 # Wait 30s, then 60s
            print(f"   🛑 Quota hit for {course_title}. Waiting {wait_time}s to retry...")
            time.sleep(wait_time)
            
        except Exception as e:
            print(f"   🚨 Unexpected error: {e}")
            break
    return None

def process_all_courses(input_file="courses.json", output_file="scored_courses.json"):
    with open(input_file, "r") as f:
        all_courses = json.load(f)

    # Load existing results to skip what we've already done
    results = {}
    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            results = json.load(f)

    print(f"🚀 Processing {len(all_courses)} courses with {MODEL_ID}...")

    # Load our external reviews file
    with open("user_reviews.json", "r") as f:
        review_data = json.load(f)

    for index, data in enumerate(all_courses):
        title = data.get('title')
        if not title or title in results:
            continue

        print(f"[{index+1}/{len(all_courses)}] Analyzing: {title}")
        
        # Pull the reviews we scraped earlier
        actual_reviews = review_data.get(title, [])
        
        # Use our new retry wrapper
        scores = analyze_with_retry(title, actual_reviews)
        
        if scores:
            results[title] = {
                "features": scores,
                "url": data.get('url', '')
            }
            # Save progress immediately
            with open(output_file, "w") as f:
                json.dump(results, f, indent=4)
        
        # Respect the 2.5-tier limit (10-15 requests per minute)
        time.sleep(6) 

if __name__ == "__main__":
    process_all_courses()