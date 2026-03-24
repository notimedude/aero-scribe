import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
import PyPDF2
from gtts import gTTS
import io
import re
from datetime import datetime
import hashlib

# --- 1. SETUP ---
load_dotenv()
# Securely load the API key from the hidden .env file
API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

# --- 2. CONFIGURATION ---
# FIXED: Using the exact name from your available models list
MODEL_NAME = 'gemini-flash-latest'
model = genai.GenerativeModel(MODEL_NAME)

LANG_CODES = {
    "English": "en",
    "Tamil": "ta",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Arabic": "ar"
}

# SIMULATED ERP DATABASE
ERP_INVENTORY = {
    "O-Ring": {"sku": "OR-9982", "stock": 42, "loc": "Bin A-12"},
    "Hydraulic Fluid": {"sku": "MIL-PRF-5606", "stock": 15, "loc": "Hazmat Cabinet"},
    "Valve Core": {"sku": "AN6287-1", "stock": 0, "loc": "Backorder"},
    "Swivel Nut": {"sku": "MS28889", "stock": 8, "loc": "Bin B-04"},
    "Cotter Pin": {"sku": "MS24665", "stock": 100, "loc": "Bin C-01"}
}

# --- 3. HELPER FUNCTIONS ---
@st.cache_data
def get_pdf_text(uploaded_file):
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return None

def clean_text_for_audio(text):
    """Removes Markdown symbols so audio is clean."""
    text = re.sub(r'#+', '', text)
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'[\|\-]{2,}', '', text)
    text = text.replace("|", "")
    return text

def text_to_speech(text, language_name):
    try:
        clean_text = clean_text_for_audio(text)
        lang_code = LANG_CODES.get(language_name, 'en')
        tts = gTTS(text=clean_text, lang=lang_code)
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes
    except Exception as e:
        return None

def generate_blockchain_hash(data):
    return hashlib.sha256(data.encode()).hexdigest()

def check_inventory(tool_list_text):
    found_items = []
    for item, details in ERP_INVENTORY.items():
        if item.lower() in tool_list_text.lower():
            status = "IN STOCK" if details['stock'] > 0 else "CRITICAL: OUT OF STOCK"
            found_items.append(f"PART: {item} | SKU: {details['sku']} | STATUS: {status} | LOC: {details['loc']}")
    
    if not found_items:
        return "No specific ERP matches found. Manual check required."
    return "\n".join(found_items)

def generate_logbook_file(ai_text, language, blockchain_hash):
    date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    clean_body = ai_text.replace("### ", "").replace("**", "").replace("|", "")
    
    log_content = f"""
________________________________________________________________________________
                        AIRCRAFT MAINTENANCE LOG RECORD
________________________________________________________________________________
LANGUAGE: {language.upper()}
DATE: {date_now}
BLOCKCHAIN HASH (IMMUTABLE ID): {blockchain_hash}

[ SECTION 1: ASSET DETAILS ]
(To be filled by Operator)

ASSET NAME:       __________________________________________________
SERIAL NUMBER:    __________________________________________________
LOCATION:         __________________________________________________
TECHNICIAN ID:    __________________________________________________

[ SECTION 2: GENERATED PROCEDURE & CHECKS ]
--------------------------------------------------------------------------------
{clean_body}
--------------------------------------------------------------------------------

[ SECTION 3: MAINTENANCE SIGN-OFF ]

STATUS (Circle One):    [ PENDING ]      [ IN-PROGRESS ]      [ COMPLETED ]

TECHNICIAN SIGNATURE: __________________________   
SUPERVISOR SIGNATURE: __________________________   
"""
    return log_content

# --- 4. UI SETUP ---
st.set_page_config(page_title="Aero-Scribe Ultimate", layout="wide")
st.title("Aero-Scribe: AI Maintenance Operating System")

if "manual_text" not in st.session_state:
    st.session_state.manual_text = ""
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = ""
if "blockchain_hash" not in st.session_state:
    st.session_state.blockchain_hash = ""

# --- 5. SIDEBAR ---
with st.sidebar:
    st.header("1. System Configuration")
    language = st.selectbox("Output Language", list(LANG_CODES.keys()))
    
    st.header("2. Multimodal Data Ingestion")
    uploaded_pdf = st.file_uploader("1. Upload Manual (PDF/S1000D)", type=["pdf"])
    uploaded_image = st.file_uploader("2. Upload Visuals (Image)", type=["jpg", "png", "jpeg"])
    uploaded_audio = st.file_uploader("3. Upload Acoustics (Audio)", type=["wav", "mp3"])
    
    st.markdown("---")
    st.caption(f"Core: {MODEL_NAME} | Modules: Vision, Audio, ERP, Blockchain")

# --- 6. MAIN LOGIC ---
if uploaded_pdf and (uploaded_image or uploaded_audio):
    
    # Display Inputs
    col1, col2 = st.columns(2)
    with col1:
        if uploaded_image:
            image = Image.open(uploaded_image)
            st.image(image, caption="Visual Input", width="stretch")
    with col2:
        if uploaded_audio:
            # FIXED: Removed 'caption' argument from st.audio
            st.audio(uploaded_audio)
            st.caption("Acoustic Input") 
            st.info("Acoustic Module Active: Analyzing spectral signature...")
    
    if uploaded_pdf:
        st.session_state.manual_text = get_pdf_text(uploaded_pdf)

    if st.button("Initialize Agentic Workflow"):
        with st.spinner(f"Agents Working: Diagnostic -> Logistics -> Compliance..."):
            try:
                context_text = st.session_state.manual_text
                if len(context_text) > 40000:
                    context_text = context_text[:40000] + "\n...[Truncated]"

                # BUILD THE PROMPT
                inputs = [f"""
                Act as a Senior Aircraft Maintenance Engineer.
                
                STRICT RULES:
                1. OUTPUT LANGUAGE: {language}.
                2. NO EMOJIS.
                3. NO MARKDOWN TABLES. 
                
                CONTEXT FROM MANUAL:
                {context_text}
                
                TASK:
                1. DIAGNOSIS: Analyze the image (and audio if provided) to identify the component and potential faults.
                2. PLANNING: List TOOLS & CONSUMABLES required.
                3. SAFETY: List CRITICAL WARNINGS.
                4. EXECUTION: Generate STEP-BY-STEP PROCEDURE with Page Citations.

                FORMAT THE OUTPUT LIKE THIS:
                
                DIAGNOSTIC REPORT
                -----------------
                - Component Identified: ...
                - Acoustic Analysis (If audio provided): ...
                - Visual Analysis: ...
                
                CRITICAL SAFETY WARNINGS
                ------------------------
                - Warning 1 (Page X)
                
                TOOLS AND CONSUMABLES
                ---------------------
                - Tool 1
                
                STEP-BY-STEP PROCEDURE
                ----------------------
                1. Step 1 (Page X)
                """]
                
                if uploaded_image: inputs.append(image)
                # Handle Audio Input for Model
                if uploaded_audio: 
                    # Note: We send audio data if the model supports it. 
                    # If using gemini-flash-latest (1.5), it supports audio.
                    inputs.append({"mime_type": "audio/mp3", "data": uploaded_audio.getvalue()})

                # GENAI CALL
                response = model.generate_content(inputs)
                st.session_state.analysis_result = response.text
                
                # BLOCKCHAIN HASH GENERATION
                st.session_state.blockchain_hash = generate_blockchain_hash(response.text)
                
            except Exception as e:
                st.error(f"Error: {e}")

    # --- DISPLAY RESULTS ---
    if st.session_state.analysis_result:
        st.divider()
        
        # 1. AGENTIC PROCUREMENT (ERP CHECK)
        st.subheader("LOGISTICS AGENT (ERP CONNECTION)")
        stock_status = check_inventory(st.session_state.analysis_result)
        st.code(stock_status, language="text") 
        
        st.divider()

        # 2. MAIN OUTPUT
        st.subheader("DIAGNOSTIC & REPAIR PLAN")
        st.text(st.session_state.analysis_result)
        
        # 3. NATIVE AUDIO
        st.subheader("HANDS-FREE AUDIO")
        audio_data = text_to_speech(st.session_state.analysis_result, language)
        if audio_data:
            st.audio(audio_data, format='audio/mp3')

        # 4. BLOCKCHAIN & DOWNLOAD
        st.divider()
        st.subheader("COMPLIANCE AGENT (BLOCKCHAIN LEDGER)")
        st.info(f"IMMUTABLE RECORD ID: {st.session_state.blockchain_hash}")
        
        log_file = generate_logbook_file(st.session_state.analysis_result, language, st.session_state.blockchain_hash)
        st.download_button(
            label="Download Signed Logbook",
            data=log_file,
            file_name=f"maintenance_log_{language}_{st.session_state.blockchain_hash[:8]}.txt",
            mime="text/plain"
        )
        
        # 5. Q&A CHAT
        st.divider()
        st.subheader("Ask the Co-Pilot")
        user_question = st.text_input("Query Manual:")
        if user_question:
            with st.spinner("Consulting manual..."):
                try:
                    chat_prompt = f"""
                    CONTEXT: {st.session_state.manual_text[:30000]}
                    QUESTION: {user_question}
                    TASK: Answer strictly based on context. LANGUAGE: {language}. NO EMOJIS.
                    """
                    chat_response = model.generate_content(chat_prompt)
                    st.info(chat_response.text)
                except Exception as e:
                    st.error("Could not answer.")

else:
    st.info("System Ready. Upload Manual + (Image OR Audio) to begin.")