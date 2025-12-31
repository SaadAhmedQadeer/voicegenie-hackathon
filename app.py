import streamlit as st
import google.generativeai as genai
import requests

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="VoiceGenie", page_icon="🎙️")

st.title("🎙️ VoiceGenie: The Speaking AI")

# --- SIDEBAR: API KEYS ---
st.sidebar.header("Configuration")
google_api_key = st.sidebar.text_input("Google Gemini API Key", type="password")
elevenlabs_api_key = st.sidebar.text_input("ElevenLabs API Key", type="password")

# --- AUTO-FIX FUNCTIONS ---

def get_working_gemini_model(api_key):
    """Try to find a working model automatically."""
    try:
        genai.configure(api_key=api_key)
        # Priority list of models to try
        candidates = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-1.0-pro', 'gemini-pro']
        
        # 1. Try to list models explicitly
        available_models = []
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
        except:
            pass # If listing fails, we just try the candidates blindly

        # 2. Match candidates against available ones (or just try them)
        for candidate in candidates:
            # Check if this candidate is in the available list (if we have one)
            # OR just try to use it if listing failed.
            model = genai.GenerativeModel(candidate)
            try:
                # Test the model with a tiny prompt
                model.generate_content("Hi")
                return candidate # It worked!
            except:
                continue # Try next one
        
        return None # No models worked
    except Exception as e:
        return None

def get_gemini_response(prompt, api_key, model_name):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Gemini Error: {str(e)}"

def text_to_speech(text, api_key):
    # VOICE ID: Rachel (Standard US English)
    url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    data = {
        "text": text,
        # IMPORTANT: This model IS available on free tier
        "model_id": "eleven_multilingual_v2", 
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return response.content
        else:
            return f"ElevenLabs API Error: {response.text}"
    except Exception as e:
        return f"Connection Error: {str(e)}"

# --- MAIN APP LOGIC ---

user_input = st.text_area("Ask me anything:", "Tell me a fun fact about coding.")

if st.button("Generate Response"):
    if not google_api_key or not elevenlabs_api_key:
        st.error("❌ Please enter both API keys in the sidebar.")
    else:
        # 1. FIND WORKING MODEL
        with st.spinner("Connecting to Google..."):
            # We try to find a valid model dynamically
            valid_model = get_working_gemini_model(google_api_key)
        
        if not valid_model:
            st.error("❌ Could not find a working Gemini model. Check your API Key.")
        else:
            st.success(f"Connected to: {valid_model}")
            
            # 2. GET TEXT
            with st.spinner(f"Thinking ({valid_model})..."):
                ai_text = get_gemini_response(user_input, google_api_key, valid_model)
            
            if "Gemini Error" in ai_text:
                st.error(ai_text)
            else:
                st.write(ai_text)
                
                # 3. GET VOICE
                with st.spinner("Synthesizing Voice..."):
                    audio_result = text_to_speech(ai_text, elevenlabs_api_key)
                
                if isinstance(audio_result, bytes):
                    st.audio(audio_result, format="audio/mp3")
                    st.success("Done!")
                else:
                    st.error(audio_result)
