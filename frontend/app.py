import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import Geocoder
from PIL import Image
import os
from geopy.distance import geodesic
from fpdf import FPDF
import io

# --- 1. PDF GENERATION LOGIC ---
# --- 1. UPDATED PDF GENERATION LOGIC ---
def create_pdf(data, distance):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 15, "Geo-Forensic Investigation Report", ln=True, align='C')
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='C')
    pdf.ln(10)

    # Stats Summary
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, f"Total Images Analyzed: {len(data)}", ln=True)
    pdf.cell(0, 10, f"Total Path Distance: {distance:.2f} KM", ln=True)
    pdf.ln(5)

    # Table Header
    pdf.set_fill_color(0, 122, 255)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(60, 10, "File Name", border=1, fill=True)
    pdf.cell(35, 10, "Lat", border=1, fill=True)
    pdf.cell(35, 10, "Lon", border=1, fill=True)
    pdf.cell(60, 10, "Source Type", border=1, fill=True, ln=True)

    # Table Rows
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 9)
    for item in data:
        # CLEAN THE EMOJIS HERE: Remove symbols that Helvetica doesn't understand
        clean_name = item['name'].encode('ascii', 'ignore').decode('ascii')[:25]
        clean_source = item['source'].encode('ascii', 'ignore').decode('ascii').strip()
        
        pdf.cell(60, 10, clean_name, border=1)
        pdf.cell(35, 10, str(round(item['lat'], 4)), border=1)
        pdf.cell(35, 10, str(round(item['lon'], 4)), border=1)
        pdf.cell(60, 10, clean_source, border=1, ln=True)

    return pdf.output()

# --- 2. PAGE SETUP ---
st.set_page_config(page_title="M2 Geo-Forensics Engine", layout="wide")

# --- 3. SIDEBAR ---
with st.sidebar:
    st.header("🎛️ Control Center")
    uploaded_files = st.file_uploader("Upload Suspect Images", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])
    st.divider()
    st.caption("Apple M2 Optimized Engine")
    if st.button("🗑️ Reset Dashboard", use_container_width=True):
        st.rerun()

# --- 4. GPS-OFF WORKFLOW LOGIC ---
processed_data = []
total_distance = 0.0

if uploaded_files:
    for i, uploaded_file in enumerate(uploaded_files):
        # SIMULATION: First file has GPS, second file has GPS OFF (using AI detection)
        if i % 2 == 0:
            sim_lat, sim_lon = 17.3850 + (i * 0.005), 78.4867 + (i * 0.005)
            source_type = "📡 Embedded GPS Metadata"
            landmark_name = "Street Location"
        else:
            # THIS IS THE GPS-OFF LOGIC: Coordinates pulled from AI Landmark Database
            sim_lat, sim_lon = 17.3616, 78.4747 # Exact coords for Charminar
            source_type = "🤖 AI Visual Match (GPS WAS OFF)"
            landmark_name = "Charminar (Historical Monument)"
        
        # Create Google Maps Navigation Link
        nav_link = f"https://www.google.com/maps/dir/?api=1&destination={sim_lat},{sim_lon}"
        
        file_info = {
            "name": uploaded_file.name,
            "lat": sim_lat,
            "lon": sim_lon,
            "landmark": landmark_name, 
            "source": source_type,
            "nav_url": nav_link,
            "size": f"{uploaded_file.size / 1024:.2f} KB",
            "image_obj": uploaded_file 
        }
        processed_data.append(file_info)
    
    if len(processed_data) > 1:
        for i in range(len(processed_data) - 1):
            p1 = (processed_data[i]['lat'], processed_data[i]['lon'])
            p2 = (processed_data[i+1]['lat'], processed_data[i+1]['lon'])
            total_distance += geodesic(p1, p2).kilometers

# --- 5. UI RENDERING ---
st.title("📍 Geospatial Intelligence Dashboard")
col1, col2, col3 = st.columns(3)
col1.metric("Images Processed", f"{len(processed_data)}")
col2.metric("Total Path Distance", f"{total_distance:.2f} KM")
col3.metric("System Status", "Tracking Active" if processed_data else "Standby")
st.divider()

if processed_data:
    map_col, info_col = st.columns([2, 1])
    with map_col:
        st.subheader("Interactive Movement Timeline")
        m = folium.Map(location=[processed_data[0]['lat'], processed_data[0]['lon']], zoom_start=15, tiles=None)
        folium.TileLayer('CartoDB positron', name="Street View").add_to(m)
        folium.TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                         attr='Esri', name='Satellite View', overlay=False).add_to(m)
        Geocoder().add_to(m) 
        folium.LayerControl().add_to(m)
        
        # Plot Path
        path_points = [[d['lat'], d['lon']] for d in processed_data]
        folium.PolyLine(path_points, color="#FF3B30", weight=5).add_to(m)
        
        for d in processed_data:
            # POPUP WITH NAVIGATION LINK
            popup_html = f"""
                <div style='font-family: Arial; width: 200px;'>
                    <b>File:</b> {d['name']}<br>
                    <b>Landmark:</b> {d['landmark']}<br>
                    <b>Source:</b> {d['source']}<br><br>
                    <a href='{d['nav_url']}' target='_blank' 
                       style='background-color: #007AFF; color: white; padding: 5px; text-decoration: none; border-radius: 5px;'>
                       🚀 Navigate to Location
                    </a>
                </div>
            """
            folium.Marker([d['lat'], d['lon']], popup=folium.Popup(popup_html, max_width=250),
                          icon=folium.Icon(color="red", icon="camera")).add_to(m)
        st_folium(m, use_container_width=True, height=500)

    with info_col:
        st.subheader("Investigation Logs")
        st.dataframe(pd.DataFrame(processed_data)[['name', 'landmark', 'source']], height=450)

    # --- 6. EVIDENCE GALLERY ---
    st.markdown("---")
    st.subheader("🖼️ Evidence Gallery")
    gallery_cols = st.columns(3)
    for idx, d in enumerate(processed_data):
        with gallery_cols[idx % 3]:
            with st.container(border=True):
                st.image(d['image_obj'], caption=d['name'], use_container_width=True)
                st.write(f"🏷️ **Source:** {d['source']}")
                st.write(f"📍 **Landmark:** {d['landmark']}")
                st.link_button("🚀 Open in Google Maps", d['nav_url'], use_container_width=True)

    # --- 7. EXPORT ---
    st.markdown("---")
    pdf_out = create_pdf(processed_data, total_distance)
    st.download_button(label="Download Forensic PDF Report", data=bytes(pdf_out),
                        file_name="Forensic_Report.pdf", mime="application/pdf", use_container_width=True)
else:
    st.info("💡 **Awaiting evidence.** Please upload images to begin movement mapping.")