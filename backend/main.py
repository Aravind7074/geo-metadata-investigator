import os
from extractor import process_image # This is the function we built in Step 4
from map_generator import generate_movement_map

def run_investigation(folder_path):
    all_results = []
    
    # Loop through images in your folder
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            print(f"Processing {filename}...")
            img_path = os.path.join(folder_path, filename)
            
            result = process_image(img_path)
            if result["lat"] and result["lng"]:
                all_results.append(result)

    # Sort by time (Backend logic for "Movement Pattern")
    # Note: If time is missing, you may need a default or skip sorting
    all_results.sort(key=lambda x: str(x['time']))

    # Generate the final map
    generate_movement_map(all_results)

if __name__ == "__main__":
    # Create a folder named 'test_images' on your MSI and put 2-3 photos there
    run_investigation("test_images")