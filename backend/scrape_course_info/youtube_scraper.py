import urllib.request
import re
import json
import os

KEYWORDS = ["Python Programming", "SQL Databases", "Cybersecurity"] # Shortened for testing

def timestamp_to_minutes(ts):
    parts = ts.split(':')
    try:
        if len(parts) == 3: return int(parts[0]) * 60 + int(parts[1])
        if len(parts) == 2: return int(parts[0])
    except: return 0
    return 0

def fetch_youtube_manual():
    unique_courses_by_id = {} 
    
    # 1. PATH CHECK: Let's see where the script thinks it is
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.abspath(os.path.join(script_dir, ".."))
    output_path = os.path.join(backend_dir, 'youtube_courses.json')
    
    print(f"📂 Current Script Directory: {script_dir}")
    print(f"🎯 Target Save Path: {output_path}")

    for query in KEYWORDS:
        print(f"\n🔍 Searching for: {query}...")
        try:
            search_query = query.replace(" ", "+") + "+full+course"
            url = f"https://www.youtube.com/results?search_query={search_query}"
            
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req) as response:
                html = response.read().decode('utf-8', errors='ignore')

            # 2. CONTENT CHECK: Did we actually get HTML back?
            if "videoRenderer" not in html:
                print("   ❌ Error: YouTube returned a page without video data. Might be a bot check.")
                continue

            raw_chunks = html.split('{"videoRenderer":')[1:]
            print(f"   📦 Found {len(raw_chunks)} potential video blocks.")

            for chunk in raw_chunks:
                block = chunk[:3500]
                id_match = re.search(r'"videoId":"([^"]+)"', block)
                if not id_match: continue
                v_id = id_match.group(1)

                if v_id in unique_courses_by_id: continue

                title_match = re.search(r'"title":\{.*?"text":"([^"]+)"', block)
                v_title = title_match.group(1).replace('\\u0026', '&') if title_match else "Unknown"

                # Check multiple channel name locations
                channel_match = re.search(r'"(?:longBylineText|ownerText)":\{.*?"text":"([^"]+)"', block)
                v_channel = channel_match.group(1).replace('\\u0026', '&') if channel_match else "YouTube Creator"

                dur_match = re.search(r'"lengthText":\{.*?"simpleText":"([\d:]+)"\}', block)
                v_duration = timestamp_to_minutes(dur_match.group(1)) if dur_match else 0

                # 3. INDIVIDUAL LOGGING: Confirm we are actually building the dictionary
                unique_courses_by_id[v_id] = {
                    "title": v_title,
                    "provider": "YouTube",
                    "url": f"https://www.youtube.com/watch?v={v_id}",
                    "thumbnail_url": f"https://i.ytimg.com/vi/{v_id}/hqdefault.jpg",
                    "partner_institution": v_channel,
                    "duration_minutes": v_duration
                }
            
            print(f"   ✅ Successfully extracted data for {query}")

        except Exception as e:
            print(f"   ⚠️ Exception during search: {e}")

    # 4. FINAL SAVE CHECK: 
    if len(unique_courses_by_id) > 0:
        print(f"\n💾 Attempting to save {len(unique_courses_by_id)} courses...")
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(list(unique_courses_by_id.values()), f, indent=4, ensure_ascii=False)
            print(f"🚀 SUCCESS! File updated at {output_path}")
        except Exception as e:
            print(f"❌ WRITE ERROR: Could not save file. {e}")
    else:
        print("\n🚫 SAVE CANCELLED: No video data was collected.")

if __name__ == "__main__":
    fetch_youtube_manual()