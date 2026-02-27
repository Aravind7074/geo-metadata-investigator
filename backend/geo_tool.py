import os, exifread, folium
from google.cloud import vision

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key.json"

def process_images(folder):
    all_pts = []
    client = vision.ImageAnnotatorClient()
    
    for f in os.listdir(folder):
        path = os.path.join(folder, f)
        # 1. Try EXIF
        with open(path, 'rb') as img:
            tags = exifread.process_file(img)
            lat = tags.get('GPS GPSLatitude')
            if lat:
                # Add extraction logic here if needed
                print(f"✅ Found EXIF for {f}")
            else:
                # 2. Try AI Fallback
                print(f"🔍 Checking AI for {f}...")
                with open(path, "rb") as i:
                    res = client.landmark_detection(image=vision.Image(content=i.read()))
                    if res.landmark_annotations:
                        lm = res.landmark_annotations[0]
                        all_pts.append({'lat': lm.locations[0].lat_lng.latitude, 'lng': lm.locations[0].lat_lng.longitude, 'name': lm.description})
                        print(f"📍 AI found: {lm.description}")

    if all_pts:
        m = folium.Map(location=[all_pts[0]['lat'], all_pts[0]['lng']], zoom_start=10)
        for p in all_pts:
            folium.Marker([p['lat'], p['lng']], popup=p['name']).add_to(m)
        m.save("final_investigation.html")
        print("🚀 SUCCESS! Open final_investigation.html")

process_images("test_images")