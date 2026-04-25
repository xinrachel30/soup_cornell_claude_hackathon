import json
import time
import os
import re
from ddgs import DDGS

BOILERPLATE_BLACKLIST = [
    "find helpful learner reviews",
    "read stories and highlights",
    "enroll for free",
    "offered by",
    "skills you'll gain",
    "why should you take",
    "how do i become",
    "how do i learn",
    "40% off",
    "annual plan", "coursera coach", "smarter way to learn", 
    "limited time", "special offer", "go to class", "start your review",
    "view details", "rating at coursera", "offered by", "financial aid"
]

# Words that usually indicate someone ASKING a question, not ANSWERING one
QUESTION_TRIGGERS = [
    "is it worth", "should i", "has anyone", "any recommendations", 
    "worth the money", "advice?", "help me decide"
]

def is_actually_a_review(text):
    text_lower = text.lower()
    
    if any(phrase in text_lower for phrase in BOILERPLATE_BLACKLIST):
        return False
    
    # 2. Kill "Questions" (Intent Filter)
    # If it has a lot of question marks or starts with "Should I", it's noise
    if text.count('?') > 1 or any(q in text_lower for q in QUESTION_TRIGGERS):
        return False
    
    # 3. Kill very short fragments
    if len(text.split()) < 10:
        return False
        
    return True

def get_high_signal_reviews(course_title):
    query = f'"{course_title}" ("my experience" OR "honest review" OR "worth it") site:reddit.com'
    
    print(f"   🔍 Hunting for real talk: {course_title}")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=12))
            
            clean_snippets = []
            for r in results:
                body = r.get('body', '')
                
                # Apply our new filters
                if is_actually_a_review(body):
                    # Clean up double spaces and newlines
                    body = re.sub(r'\s+', ' ', body).strip()
                    clean_snippets.append(body)
            
            return clean_snippets
    except Exception as e:
        print(f"   🚨 Search Error: {e}")
        return []


def main():
    # Load your courses
    with open("courses.json", "r") as f:
        courses = json.load(f)

    output_file = "user_reviews.json"
    
    # Load existing to resume if you stop it
    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            review_data = json.load(f)
    else:
        review_data = {}

    print(f"🚀 Starting Multi-Source Review Fetcher for {len(courses)} courses...")

    for index, course in enumerate(courses):
        title = course.get('title')
        if not title or title in review_data:
            continue

        print(f"[{index+1}/{len(courses)}] Processing: {title}")
        
        real_quotes = get_high_signal_reviews(title)
        
        if real_quotes:
            print(f"   ✅ Found {len(real_quotes)} potential human signals!")
            review_data[title] = real_quotes
            
            # Save every 5 courses to reduce disk writing but keep progress
            if index % 5 == 0:
                with open(output_file, "w") as f:
                    json.dump(review_data, f, indent=4)
        else:
            print("No high-signal snippets found for this query.")
        
        # Delay to avoid being flagged by DuckDuckGo
        time.sleep(3)

    # Final Save
    with open(output_file, "w") as f:
        json.dump(review_data, f, indent=4)
    print(f"\n✅ All done! Data saved to {output_file}")

if __name__ == "__main__":
    main()