import streamlit as st
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

# Load API Key
load_dotenv()
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

# --- HARMLESS BRANDING & UI SETUP ---
st.set_page_config(page_title="Harmless Diagnostic", layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #f4f6f9; }
    h1 { color: #000399; font-weight: bold; border-bottom: 4px solid #FFC107; padding-bottom: 10px; }
    .stButton>button { background-color: #000399; color: white; border: none; width: 100%; font-weight: bold; }
    .stButton>button:hover { background-color: #121212; color: #FFC107; }
    .custom-card { padding: 20px; border-radius: 8px; background: white; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 6px solid #000399; }
    .summary-card { border-left-color: #D32F2F; }
    .assessment-card { border-left-color: #FFC107; }
    </style>
""", unsafe_allow_html=True)

st.title("Harmless Diagnostic")
# Bridged subheader for both classroom and out-of-school children
st.subheader("Diagnostic & Retention Tool for Ghanaian Educators")

# --- DATA INPUT FORM ---
with st.form("diagnostic_form"):
    st.write("**Assessment Context:**")
    
    col1, col2, col3 = st.columns(3)
    # Added "Out-of-School Re-entry" to the level options to hit the target requirement
    with col1: class_level = st.selectbox("Student Level", 
        ["JHS 1", "JHS 2", "JHS 3", "SHS 1", "SHS 2", "SHS 3", "TVET", "Out-of-School Re-entry"])
    with col2: subject = st.text_input("Subject", placeholder="e.g., Numeracy / Literacy")
    with col3: strand_topic = st.text_input("Strand / Topic", placeholder="e.g., Word Recognition")
    
    col4, col5 = st.columns(2)
    with col4: student_count = st.number_input("Total Students in Group", min_value=1, value=1)
    with col5: focus_type = st.selectbox("Diagnostic Focus", ["Classroom Gap", "Enrolment Placement", "Retention Support"])
    
    teacher_observation = st.text_area("Observation (What is the child's current struggle or skill level?)")
    
    submitted = st.form_submit_button("Generate Bridged Diagnostic Plan")

# --- AI PROCESSING ---
if submitted:
    if not os.environ.get("GEMINI_API_KEY"):
        st.error("API Key missing! Please check your settings.")
    else:
        with st.spinner("Analyzing data for enrolment and learning retention..."):
            try:
                # Bridged System Prompt combining Challenge 1 and the Out-of-School requirement
                system_prompt = f"""
                You are the intelligence core of "Harmless Diagnostic," a tool designed for the UNICEF StartUp Lab Challenge.
                
                DUAL MISSION:
                1. CLASSROOM: Help JHS/SHS/TVET teachers identify foundation-level literacy/numeracy gaps in current students.
                2. OUT-OF-SCHOOL: Support the enrolment, retention, and learning of out-of-school children by diagnosing their current level and providing remedial re-entry paths.
                
                CRITICAL CONSTRAINTS:
                - Focus on "Enrolment, Retention, and Learning".
                - Remedial activities must be "Zero-Tech" using locally available materials.
                - Format strictly as JSON.

                INPUT DATA:
                - Level/Context: {class_level}
                - Subject: {subject}
                - Topic: {strand_topic}
                - Focus Type: {focus_type}
                - Observation: {teacher_observation}

                YOUR REQUIRED JSON OUTPUT FORMAT:
                {{
                  "diagnostic_summary": "One sentence identifying the core learning or re-entry gap.",
                  "nacca_alignment": "Connect this to a NaCCA competency for tracking purposes.",
                  "low_resource_activity": {{
                    "title": "Remedial activity for retention.",
                    "materials_needed": "1-3 free, local items.",
                    "step_by_step": ["Step 1", "Step 2", "Step 3"]
                  }},
                  "quick_assessment": "5-minute offline check to verify learning progress."
                }}
                """

                response = model.generate_content(system_prompt)
                
                # Clean and parse JSON
                response_text = response.text.strip()
                if response_text.startswith("```json"):
                    response_text = response_text[7:-3].strip()
                elif response_text.startswith("```"):
                    response_text = response_text[3:-3].strip()
                    
                result = json.loads(response_text)

                # --- DISPLAY RESULTS ---
                st.success("Analysis Complete!")
                
                st.markdown(f"""
                <div class="custom-card summary-card">
                    <h3 style="color:#121212; margin-top:0;">Diagnostic & Retention Summary</h3>
                    <p><b>Issue:</b> {result['diagnostic_summary']}</p>
                    <p style="font-size: 0.9em; color: #555;"><i>Tracking Alignment: {result['nacca_alignment']}</i></p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="custom-card">
                    <h3 style="color:#000399; margin-top:0;">{result['low_resource_activity']['title']}</h3>
                    <p><b>Materials Needed:</b> {result['low_resource_activity']['materials_needed']}</p>
                    <b>Remedial Steps for Retention:</b>
                    <ul>
                        {''.join([f"<li>{step}</li>" for step in result['low_resource_activity']['step_by_step']])}
                    </ul>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="custom-card assessment-card">
                    <h3 style="color:#121212; margin-top:0;">Quick Offline Assessment</h3>
                    <p>{result['quick_assessment']}</p>
                </div>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Analysis failed. Please refine your observation and try again.") 