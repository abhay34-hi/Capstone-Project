import streamlit as st
from google import genai # The new library
import random 
import time
from datetime import datetime
import nlu_model 

# --- 1. CONFIGURATION: PASTE YOUR KEY HERE ---
# ⚠️ REPLACE "YOUR_GEMINI_API_KEY_HERE" WITH YOUR ACTUAL KEY (AIzaSy...)
GEMINI_API_KEY = "AZS" 

# --- 2. Initialize the Gemini AI Client (STABLE SOLUTION) ---
# We use cache_resource to ensure it only initializes once per session.
@st.cache_resource(show_spinner=False)
def initialize_gemini_client(api_key):
    # 1. Integrity Check
    if not api_key or not api_key.startswith("AIza"):
        return None 
    try:
        # 2. Initialize the client
        client = genai.Client(api_key=api_key)
        
        # 3. Quick Validation Test: Check the model list to ensure connection is live
        list(client.models.list())
        return client
    except Exception as e:
        return None

client = initialize_gemini_client(GEMINI_API_KEY)

# --- DUMMY JOB DATA (For context awareness) ---
# (Minimal set to prevent crashing if app.py data is missed)
JOBS_DB_MINIMAL = {
    "j1": {"title": "Senior Clerk (Govt)", "dept": "Water Supply", "loc": "Patiala", "sal": "₹35k", "reqs": ["Graduate"]},
    "j2": {"title": "School Teacher", "dept": "Education Dept", "loc": "Ludhiana", "sal": "₹42k", "reqs": ["B.Ed / ETT"]},
}

# --- 3. THE "HYBRID" BRAIN FUNCTION (REVISED FOR BERT-LIKE ACCURACY) ---
def get_hybrid_response(user_query, user_name, lang, app_history, job_list):
    
    if not client:
        return "Error: AI service is currently offline. Please ensure the GEMINI API Key is correct."

    # Handle Simple Greeting (Hardcoded for speed)
    query_lower = user_query.lower()
    if any(word in query_lower for word in ["hi", "hello", "hey", "hola", "sat sri akal", "namaste"]):
        if lang == 'hi': return f"नमस्ते {user_name}! मैं आपकी कैसे मदद कर सकता हूँ?"
        elif lang == 'pa': return f"ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ {user_name}! ਮੈਂ ਤੁਹਾਡੀ ਕਿਵੇਂ ਮਦਦ ਕਰ ਸਕਦਾ ਹਾਂ?"
        else: return f"Hello {user_name}! How can I help you today?"

    # --- SIMULATE BERT/NLU AND DIALOGUE MANAGER WITH A SINGLE, POWERFUL PROMPT ---
    jobs_to_use = job_list if job_list else JOBS_DB_MINIMAL
    jobs_text = "\n".join([f"- {job['title']} in {job['loc']} ({job['sal']})" for j_id, job in jobs_to_use.items()])
    
    app_text = "No active applications found."
    if app_history: 
        # Format the application history for clear LLM reference
        app_text = "\n".join([f"- {app.get('title', 'Unknown Job')} (Status: {app.get('status', 'N/A')})" for app in app_history])
        
    prompt = f"""
    You are a highly accurate, multilingual AI assistant for the PUNJAB ROZGAR (PGRKAM) job portal. 
    **Your primary task is to act as both an Intent Classifier (like BERT) and a helpful Dialogue Manager.**

    **Current Context:**
    - User Name: {user_name}
    - User Language: {lang}
    - Available Job Listings: {jobs_text}
    - User's Application History: {app_text}

    **Core Instructions for Response Generation:**
    1.  **Intent Classification (BERT Role):** Accurately determine the user's hidden intent (e.g., Job Search, Application Status, Career Advice).
    2.  **Contextual Response:** If the intent is Job Search or Status, **strictly use the provided context.** Do not invent jobs or application statuses.
    3.  **Proactive (Slot-Filling Role):** If the intent is Job Search, but the user has **not** mentioned a **Location** or a **Keyword**, politely ask for that missing information to narrow down the results.
    4.  **Language:** Respond ONLY in the user's language ({lang}). Keep the response friendly, concise, and professional.

    **User Query:** '{user_query}'
    """
    
    return call_gemini(prompt)

# ... rest of chatbot.py (call_gemini function) ...
# --- 4. THE API CALLER ---
def call_gemini(prompt):
    if not client:
        return "Error: AI service is not running. Check API key."
        
    try:
        # Use a model capable of quick, conversational responses and multilingual output
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Error connecting to AI: {e}"