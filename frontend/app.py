import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import pipeline  # 🧠 YOUR BACKEND CONNECTION
from fpdf import FPDF
import io

# --- 1. PAGE SETUP & CYBER-THEME ---
st.set_page_config(page_title="M2 Geo-Forensics Engine", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #e0e0e0; font-family: 'Courier New', Courier, monospace; }
    
    section[data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(0, 242, 255, 0.2);
    }

    [data-testid="stMetricValue"] { color: #00f2ff !important; text-shadow: 0 0 10px rgba(0, 242, 255, 0.5); }
    
    div[data-testid="stElementContainer"] > div[style*="border"] {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(0, 242, 255, 0.15) !important;
        border-radius: 10px !important;
    }

    .terminal-box {
        background: rgba(0, 0, 0, 0.7); color: #00ff41; padding: 10px;
        font-size: 0.8rem; border-left: 2px solid #00ff41; margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIC: PDF GENERATION ---
def create_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    def clean_text(text): return str(text).encode('ascii', 'ignore').decode('ascii').strip()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 15, "Geo-Forensic Intelligence Report", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, f"Evidence Nodes: {len(data)}", ln=True)
    pdf.set_fill_color(0, 150, 255); pdf.set_text_color(255, 255, 255)
    
    # Dynamic columns based on your extracted_data keys
    pdf.cell(80, 10, "File Name", 1, 0, 'C', True)
    pdf.cell(50, 10, "Coordinates", 1, 0, 'C', True)
    pdf.cell(60, 10, "Source/Status", 1, 1, 'C', True)
    
    pdf.set_text_color(0, 0, 0); pdf.set_font("Helvetica", "", 10)
    for index, row in data.iterrows():
        pdf.cell(80, 10, clean_text(row.get('File', 'Unknown'))[:30], 1)
        pdf.cell(50, 10, clean_text(f"{row.get('Lat', 0)}, {row.get('Lon', 0)}"), 1)
        pdf.cell(60, 10, clean_text(row.get('Source', 'AI Detected')), 1, 1)
    return pdf.output()

# --- 3. SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("<h2 style='color:#00f2ff;'>🛡️ RECON CORE</h2>", unsafe_allow_html=True)
    # The file uploader is the "test_images" source for the pipeline
    uploaded_files = st.file_uploader("Inject Forensic Media", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])
    st.divider()
    st.info("System optimized for MacBook M2 Neural Engine.")

# --- 4. MAIN DASHBOARD ---
st.title("📍 GEOSPATIAL FORENSIC ENGINE")
st.markdown("<p style='color:#00f2ff; margin-top:-20px;'>Advanced Movement Tracking & Visual Reconnaissance</p>", unsafe_allow_html=True)

if uploaded_files:
    # RUN THE AI INVESTIGATION TRIGGER
    if st.button("🚀 INITIATE AI RECONNAISSANCE", use_container_width=True):
        with st.spinner("Executing Neural Extraction Pipeline..."):
            
            # CALLING YOUR BACKEND
            # Assuming your pipeline handles the file objects directly or you save them to a temp folder
            investigation_map, extracted_data = pipeline.process_images(uploaded_files)
            
            if investigation_map and not extracted_data.empty:
                st.session_state.map = investigation_map
                st.session_state.data = extracted_data
                st.success("Analysis Complete: Neural Uplink Established.")
            else:
                st.error("Extraction Failed: No Geospatial data found in the provided evidence.")

# --- 5. UI RENDERING (AFTER PIPELINE RUNS) ---
if "map" in st.session_state:
    m1, m2 = st.columns([2.5, 1])
    
    with m1:
        st.subheader("Satellite Recon Map")
        # Display the map returned by your pipeline
        st_folium(st.session_state.map, use_container_width=True, height=550)

    with m2:
        st.subheader("Intelligence Stream")
        st.dataframe(st.session_state.data, height=510, use_container_width=True)

    # Export Section
    st.divider()
    pdf_bytes = create_pdf(st.session_state.data)
    st.download_button(
        "📂 DOWNLOAD CLASSIFIED DOSSIER (PDF)", 
        data=bytes(pdf_bytes), 
        file_name="Forensic_Analysis_Report.pdf", 
        use_container_width=True
    )
    
    if st.button("🗑️ Clear Current Investigation"):
        del st.session_state.map
        del st.session_state.data
        st.rerun()

else:
    st.info("🛰️ **System Standby.** Upload forensic images via the sidebar and click 'Initiate' to begin neural reconstruction.")

# --- TERMINAL LOG (Side-view) ---
if uploaded_files:
    st.sidebar.markdown(f"""<div class="terminal-box">
        [SYS]: {len(uploaded_files)} files ready<br>
        [GPU]: M2 Shaders Loaded<br>
        [STATUS]: Awaiting Execution
    </div>""", unsafe_allow_html=True)
