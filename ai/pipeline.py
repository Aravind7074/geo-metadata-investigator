import os
import json
import exifread
import folium
from google import genai
from PIL import Image
from dotenv import load_dotenv
import pandas as pd # <-- M3's UI expects a Pandas DataFrame

# --- ADD THIS ADAPTER FUNCTION ---
def process_uploaded_files(uploaded_files):
    """
    Adapter function for Streamlit: Takes memory files, saves them, 
    runs the AI pipeline, and returns the formatted map and dataframe.
    """
    TEMP_FOLDER = "streamlit_temp_evidence"
    
    # 1. Create a fresh temp folder
    if not os.path.exists(TEMP_FOLDER):
        os.makedirs(TEMP_FOLDER)
    else:
        # Clear out old evidence
        for f in os.listdir(TEMP_FOLDER):
            os.remove(os.path.join(TEMP_FOLDER, f))

    # 2. Save M3's memory files to the hard drive
    for file in uploaded_files:
        with open(os.path.join(TEMP_FOLDER, file.name), "wb") as f:
            f.write(file.getbuffer())

    # 3. Run YOUR existing pipeline on the new folder
    investigation_map, raw_data = process_images(TEMP_FOLDER)

    # 4. Format the data to match M3's PDF generator expectations
    if raw_data:
        # M3's UI expects keys like 'File', 'Lat', 'Lon', 'Source'
        formatted_data = []
        for item in raw_data:
            formatted_data.append({
                "File": item.get("filename", "Unknown"),
                "Lat": item.get("lat", 0.0),
                "Lon": item.get("lng", 0.0),
                "Source": item.get("source", "AI Detected")
            })
        df = pd.DataFrame(formatted_data)
    else:
        df = pd.DataFrame()

    return investigation_map, df
# ---------------------------------

# (Your original process_images function starts here)
def process_images(folder):
# ... rest of your code ...
# 1. Actually run the function to load the hidden file
load_dotenv()

# 2. Grab the key
api_key = os.getenv("GEMINI_API_KEY")

# --- CONFIGURATION --- 
client = genai.Client(api_key=api_key)
TARGET_FOLDER = "evidence_images" 

# --- QUALITY FIX: M1's Missing EXIF Math ---
def convert_to_degrees(value):
    """Converts EXIF GPS format (Degrees, Minutes, Seconds) to Decimal."""
    d, m, s = value.values
    return d.num / d.den + (m.num / m.den / 60.0) + (s.num / s.den / 3600.0)

def process_images(folder):
    all_pts = []
    
    if not os.path.exists(folder):
        print(f"Folder '{folder}' not found. Please create it.")
        return

    for f in os.listdir(folder):
        if not f.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue
            
        path = os.path.join(folder, f)
        print(f"\n[+] Processing: {f}")
        
        # ---------------------------------------------------------
        # 1. M1's EXIF EXTRACTION (Fast & Accurate)
        # ---------------------------------------------------------
        with open(path, 'rb') as img:
            tags = exifread.process_file(img)
            
        lat_tag = tags.get('GPS GPSLatitude')
        lat_ref = tags.get('GPS GPSLatitudeRef')
        lng_tag = tags.get('GPS GPSLongitude')
        lng_ref = tags.get('GPS GPSLongitudeRef')

        if lat_tag and lng_tag and lat_ref and lng_ref:
            try:
                lat = convert_to_degrees(lat_tag)
                if lat_ref.values[0] != 'N': lat = -lat
                
                lng = convert_to_degrees(lng_tag)
                if lng_ref.values[0] != 'E': lng = -lng
                
                all_pts.append({
                    'lat': lat, 
                    'lng': lng, 
                    'name': f"Verified EXIF Data",
                    'source': 'EXIF'
                })
                print(f"  ✅ Found exact EXIF coordinates!")
                continue # Skip the AI if we already have the GPS
            except Exception as e:
                print(f"  ⚠️ Error parsing EXIF: {e}")

        # ---------------------------------------------------------
        # 2. M2's GEMINI AI FALLBACK (The Brains)
        # ---------------------------------------------------------
        print(f"  🔍 No usable GPS. Booting Gemini AI...")
        try:
            img_data = Image.open(path)
            prompt = """
            Identify the landmark in this photo. Return ONLY a JSON object:
            {"name": "Landmark Name", "lat": 0.0, "lng": 0.0, "desc": "1-sentence context"}
            If unknown, return {"error": "unknown"}.
            """
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[prompt, img_data]
            )
            
            raw_text = response.text.replace('```json', '').replace('```', '').strip()
            data = json.loads(raw_text)
            
            if "error" not in data:
                all_pts.append({
                    'lat': data['lat'], 
                    'lng': data['lng'], 
                    'name': data['name'],
                    'desc': data.get('desc', ''),
                    'source': 'AI'
                })
                print(f"  📍 AI found: {data['name']}")
            else:
                print("  ❌ AI could not identify a landmark.")
        except Exception as e:
            print(f"  ⚠️ AI Error: {e}")

    # ---------------------------------------------------------
    # 3. MAPPING (Generating the Output)
    # ---------------------------------------------------------
    if all_pts:
        print("\n🗺️ Generating Investigative Map...")
        m = folium.Map(location=[all_pts[0]['lat'], all_pts[0]['lng']], zoom_start=4)
        
        for p in all_pts:
            # Color coding: Green for EXIF, Red for AI guesses
            color = "green" if p['source'] == 'EXIF ' else "red"
            icon_type = "ok-sign" if p['source'] == 'EXIF' else "camera"
            
            popup_html = f"<b>{p['name']}</b><br>Source: <b>{p['source']}</b>"
            if 'desc' in p:
                popup_html += f"<br><i>{p['desc']}</i>"
                
            folium.Marker(
                [p['lat'], p['lng']], 
                popup=popup_html,
                icon=folium.Icon(color=color, icon=icon_type)
            ).add_to(m)
            
        return m, all_pts
    else:
        print("\n⚠️ No data found to map.")
        return None, None

# --- QUALITY FIX: Stop the script from auto-running when Streamlit imports it ---
if __name__ == "__main__":
    # This only runs if you execute pipeline.py directly in your terminal
    process_images(TARGET_FOLDER)
