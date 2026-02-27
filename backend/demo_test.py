from map_generator import generate_movement_map

# Mock data representing an investigative trail in Paris
mock_timeline = [
    {
        "time": "2026:02:27 10:00:00", 
        "lat": 48.8584, 
        "lng": 2.2945, 
        "landmark_name": "Eiffel Tower", 
        "source": "EXIF Metadata"
    },
    {
        "time": "2026:02:27 12:30:00", 
        "lat": 48.8606, 
        "lng": 2.3376, 
        "landmark_name": "Louvre Museum", 
        "source": "AI Recognition"
    },
    {
        "time": "2026:02:27 15:45:00", 
        "lat": 48.8529, 
        "lng": 2.3501, 
        "landmark_name": "Notre Dame", 
        "source": "EXIF Metadata"
    },
    {
        "time": "2026:02:27 18:20:00", 
        "lat": 48.8462, 
        "lng": 2.3447, 
        "landmark_name": "Panthéon", 
        "source": "AI Recognition"
    }
]

if __name__ == "__main__":
    print("Generating Demo Map...")
    generate_movement_map(mock_timeline, output_file="demo_movement.html")
    print("Open 'demo_movement.html' in your browser to see the result!")