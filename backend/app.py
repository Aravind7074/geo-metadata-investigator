import streamlit as st
import folium
from streamlit_folium import st_folium
import json

# Set up the dashboard
st.set_page_config(page_title="Geo-Investigator", layout="wide")
st.title("🗺️ Movement Mapping Intelligence")
st.markdown("Analyzing geospatial metadata and AI-extracted landmarks.")

def load_data():
    try:
        with open("movement_data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

data = load_data()

# Filter out the images where the AI couldn't find a landmark (like the coffee mug)
valid_locations = [item for item in data if "error" not in item]

if valid_locations:
    # Center the map on the first found location
    start_lat = valid_locations[0]["lat"]
    start_lng = valid_locations[0]["lng"]
    
    m = folium.Map(location=[start_lat, start_lng], zoom_start=4, tiles="CartoDB positron")
    
    # Plot the exact coordinates you extracted!
    for loc in valid_locations:
        folium.Marker(
            location=[loc["lat"], loc["lng"]],
            popup=f"<b>{loc['name']}</b><br><i>{loc['filename']}</i><br>{loc['desc']}",
            tooltip="Click for intelligence report",
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(m)
        
    # Render map in the web app
    st_folium(m, width=900, height=500)
    
    # Show the raw JSON data below for the judges
    st.subheader("Raw Extracted Intelligence")
    st.dataframe(valid_locations)
else:
    st.warning("No geospatial data available to map. Please run the extraction module.")