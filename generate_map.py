import json
import folium
import os

def create_map():
    data_path = 'ai/movement_data.json'
    
    # 1. Check if the file even exists
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found!")
        return

    # 2. Load the JSON data
    with open(data_path, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print("Error: movement_data.json is not valid JSON!")
            return

    # 3. Create the Map (Centered on the first point)
    try:
        start_lat = data[0]['lat']
        start_lon = data[0]['lon']
        m = folium.Map(location=[start_lat, start_lon], zoom_start=4)

        # 4. Add markers for every point
        for entry in data:
            folium.Marker(
                location=[entry['lat'], entry['lon']],
                popup=f"<b>{entry['landmark']}</b><br>{entry['timestamp']}",
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(m)

        # 5. Save and Finish
        m.save("index.html")
        print("✅ SUCCESS: index.html has been generated and is ready for the judges!")
        
    except KeyError as e:
        print(f"❌ QA FAILED: The JSON is missing a key: {e}")
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")

if __name__ == "__main__":
    create_map()