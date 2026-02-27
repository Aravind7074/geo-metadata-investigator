import folium
from datetime import datetime

def generate_movement_map(data_points, output_file="movement_map.html"):
    # 1. Start the map at the first location found
    if not data_points:
        return "No data to map"
    
    start_coords = [data_points[0]['lat'], data_points[0]['lng']]
    m = folium.Map(location=start_coords, zoom_start=13, tiles="OpenStreetMap")

    # 2. Prepare coordinates for the 'Path Line'
    path_coords = []

    for point in data_points:
        coord = [point['lat'], point['lng']]
        path_coords.append(coord)
        
        # 3. Add a marker for each location
        popup_text = f"<b>{point['landmark_name']}</b><br>Time: {point['time']}<br>Source: {point['source']}"
        folium.Marker(
            location=coord,
            popup=folium.Popup(popup_text, max_width=300),
            icon=folium.Icon(color="blue" if point['source'] == "EXIF Metadata" else "red", icon="info-sign")
        ).add_to(m)

    # 4. Draw the chronological path line
    folium.PolyLine(path_coords, color="red", weight=2.5, opacity=0.8).add_to(m)

    # 5. Save the map
    m.save(output_file)
    print(f"✅ Map generated successfully: {output_file}")