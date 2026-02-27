import os
import json
from google import genai
from PIL import Image

# 1. Configuration
# Initialize the new modern client
client = genai.Client(api_key="apikey") 

IMAGE_FOLDER = "./evidence_images"  
OUTPUT_FILE = "movement_data.json"

def process_evidence_folder():
    all_results = []

    # Quality Check: Prevent crashes if the folder is missing
    if not os.path.exists(IMAGE_FOLDER):
        os.makedirs(IMAGE_FOLDER)
        print(f"Created folder: {IMAGE_FOLDER}. Drop some test images in there and run me again!")
        return

    # 2. Loop through every file in the folder
    for filename in os.listdir(IMAGE_FOLDER):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            print(f"Analyzing: {filename}...")
            
            img_path = os.path.join(IMAGE_FOLDER, filename)
            img = Image.open(img_path)

            prompt = """
            Identify the landmark in this photo. Return ONLY a JSON object:
            {"name": "Landmark Name", "lat": 0.0, "lng": 0.0, "desc": "1-sentence context"}
            If unknown, return {"error": "unknown"}.
            """
            
            try:
                # The new 2026 SDK syntax using the fastest Flash model
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[prompt, img]
                )
                
                # Clean and parse JSON
                raw_text = response.text.replace('```json', '').replace('```', '').strip()
                data = json.loads(raw_text)
                data['filename'] = filename 
                all_results.append(data)
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    # 3. Save as a single high-quality JSON file for M3 (Frontend)
    if all_results:
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(all_results, f, indent=4)
        print(f"Success! {len(all_results)} images mapped to {OUTPUT_FILE}")

process_evidence_folder()