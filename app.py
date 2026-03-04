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
st.subheader("Upper-Level Remedial Gap Analysis (JHS/SHS/TVET)")

# --- DATA INPUT FORM ---
with st.form("diagnostic_form"):
    st.write("**Enter Class Data Below:**")
    
    col1, col2, col3 = st.columns(3)
    with col1: class_level = st.selectbox("Level", ["JHS 1", "JHS 2", "JHS 3", "SHS 1", "SHS 2", "SHS 3", "TVET"])
    with col2: subject = st.text_input("Subject", placeholder="e.g., Core Mathematics")
    with col3: strand_topic = st.text_input("Strand / Topic", placeholder="e.g., Algebra")
    
    col4, col5 = st.columns(2)
    with col4: class_size = st.number_input("Total Students", min_value=1, value=45)
    with col5: struggling_count = st.number_input("Students with Foundation Gaps", min_value=1, value=15)
    
    teacher_observation = st.text_area("Observation (e.g., Struggles with primary-level multiplication, cannot read phonetically, etc.)")
    
    submitted = st.form_submit_button("Analyze Foundation Gap")

# --- AI PROCESSING ---
if submitted:
    if not os.environ.get("GEMINI_API_KEY"):
        st.error("API Key missing! Please check your settings.")
    else:
        with st.spinner("Identifying foundation-level gaps..."):
            try:
                # Updated System Prompt focused on UNICEF Challenge Statement
                system_prompt = f"""
                You are the core intelligence of "Harmless Diagnostic," a rapid diagnostic tool specifically for JHS, SHS, and TVET educators in Ghana.
                
                MISSION: Help upper-level teachers identify foundation-level literacy and numeracy gaps in students who have already exited primary school.
                
                CRITICAL CONSTRAINTS:
                1. TARGET LEVELS: JHS, SHS, and TVET.
                2. FOCUS: Foundation-level literacy/numeracy gaps (remedial strategies).
                3. LOW RESOURCE: Activities MUST NOT require internet, electricity, or expensive tools.
                4. FORMATTING: Return strictly as a valid JSON object. Do not include markdown formatting.

                INPUT DATA:
                - Level: {class_level}
                - Subject: {subject}
                - Strand/Topic: {strand_topic}
                - Teacher's Observation: {teacher_observation}

                YOUR REQUIRED JSON OUTPUT FORMAT:
                {{
                  "diagnostic_summary": "One sentence summary identifying the foundation-level cognitive block (e.g., missing Basic 3 multiplication logic).",
                  "nacca_alignment": "Brief statement connecting this remedial need to the NaCCA foundation competency.",
                  "low_resource_activity": {{
                    "title": "Short name for the remedial activity.",
                    "materials_needed": "List of 1-3 completely free, locally accessible items.",
                    "step_by_step": [
                      "Step 1: instruction",
                      "Step 2: instruction",
                      "Step 3: instruction"
                    ]
                  }},
                  "quick_assessment": "A single, 5-minute offline way to verify the foundation gap is closing."
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
                st.success("Remedial Strategy Generated!")
                
                st.markdown(f"""
                <div class="custom-card summary-card">
                    <h3 style="color:#121212; margin-top:0;">Foundation Gap Summary</h3>
                    <p><b>Issue:</b> {result['diagnostic_summary']}</p>
                    <p style="font-size: 0.9em; color: #555;"><i>Primary Foundation Alignment: {result['nacca_alignment']}</i></p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="custom-card">
                    <h3 style="color:#000399; margin-top:0;">{result['low_resource_activity']['title']}</h3>
                    <p><b>Materials Needed:</b> {result['low_resource_activity']['materials_needed']}</p>
                    <b>Remedial Step-by-Step:</b>
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
                st.error(f"Analysis failed. Please check your observation and try again.")
                