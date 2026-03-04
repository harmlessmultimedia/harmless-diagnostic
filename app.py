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
st.subheader("NaCCA-Aligned Learning Gap Analysis")

# --- DATA INPUT FORM ---
with st.form("diagnostic_form"):
    st.write("**Enter Class Data Below:**")
    
    col1, col2, col3 = st.columns(3)
    with col1: class_level = st.text_input("Basic Level", placeholder="e.g., Basic 4")
    with col2: subject = st.text_input("Subject", placeholder="e.g., Mathematics")
    with col3: strand_topic = st.text_input("Strand / Topic", placeholder="e.g., Fractions")
    
    col4, col5 = st.columns(2)
    with col4: class_size = st.number_input("Total Students", min_value=1, value=40)
    with col5: struggling_count = st.number_input("Struggling Students", min_value=1, value=15)
    
    teacher_observation = st.text_area("Teacher's Observation", placeholder="What exactly are they getting wrong?")
    
    submitted = st.form_submit_button("Analyze Gap & Get Lesson Plan")

# --- AI PROCESSING ---
if submitted:
    if not os.environ.get("GEMINI_API_KEY"):
        st.error("API Key missing! Please check your .env file.")
    else:
        with st.spinner("Analyzing learning gap against NaCCA standards..."):
            try:
                system_prompt = f"""
                You are the core intelligence of "Harmless Diagnostic," an expert educational assistant trained on the Ghana Education Service (GES) NaCCA framework.

                CRITICAL CONSTRAINTS:
                1. LOW RESOURCE ZERO-TECH: The target users are often in rural Ghanaian schools. Your suggested activities MUST NOT require internet access, tablets, electricity, or expensive printed worksheets. Use locally available materials.
                2. ALIGNMENT: Your advice must support the competency-based curriculum for the specified Basic Class.
                3. FORMATTING: You must return your analysis strictly as a valid JSON object. Do not include markdown formatting like ```json or any text outside the JSON block.

                INPUT DATA PROVIDED BY TEACHER:
                - Class Level: {class_level}
                - Subject: {subject}
                - Strand/Topic: {strand_topic}
                - Class Size: {class_size}
                - Struggling Students: {struggling_count}
                - Teacher's Observation: {teacher_observation}

                YOUR REQUIRED JSON OUTPUT FORMAT:
                {{
                  "diagnostic_summary": "One sentence summary identifying the core cognitive block.",
                  "nacca_alignment": "Brief statement connecting this gap to the NaCCA competency.",
                  "low_resource_activity": {{
                    "title": "Short name for the activity.",
                    "materials_needed": "List of 1-3 completely free, locally accessible items.",
                    "step_by_step": [
                      "Step 1: instruction",
                      "Step 2: instruction",
                      "Step 3: instruction"
                    ]
                  }},
                  "quick_assessment": "A single, 5-minute offline way to verify understanding."
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
                    <h3 style="color:#121212; margin-top:0;">Diagnostic Summary</h3>
                    <p><b>Issue:</b> {result['diagnostic_summary']}</p>
                    <p style="font-size: 0.9em; color: #555;"><i>NaCCA Alignment: {result['nacca_alignment']}</i></p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="custom-card">
                    <h3 style="color:#000399; margin-top:0;">{result['low_resource_activity']['title']}</h3>
                    <p><b>Materials Needed:</b> {result['low_resource_activity']['materials_needed']}</p>
                    <b>Step-by-Step Guide:</b>
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
                st.error(f"An error occurred: {str(e)}")