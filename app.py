import streamlit as st
import requests
import json

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="VoiceGenie: Hackathon Edition", page_icon="🎙️")
st.title("🎙️ VoiceGenie: Auto-Detect Mode")
st.write("Current Status: Detecting Models...")

# --- SIDEBAR: API KEYS ---
st.sidebar.header("Configuration")
google_api_key = st.sidebar.text_input("Google Gemini API Key", type="password")
elevenlabs_api_key = st.sidebar.text_input("ElevenLabs API Key", type="password")

# --- AUTO-DETECT FUNCTION ---
def find_working_gemini_model(api_key):
    """
    Asks Google which models are available for this specific API Key.
    """
    key = api_key.strip()
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # Iterate through all available models
            for model in data.get('models', []):
                # We need a model that supports 'generateContent'
                if 'generateContent' in model.get('supportedGenerationMethods', []):
                    # valid names come like "models/gemini-1.5-flash"
                    # We usually need just "gemini-1.5-flash" or the full string depending on the endpoint
                    return model['name'] # Returns full "models/gemini-1.5-flash"
            return None
        else:
            st.error(f"Google API Error when listing models: {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection Failed: {e}")
        return None

def get_gemini_response(prompt, api_key, model_name):
    clean_key = api_key.strip()
    # Use the model name exactly as Google gave it to us
    # The model_name already contains "models/" so we don't add it again if it's there
    if not model_name.startswith("models/"):
        model_name = f"models/{model_name}"
        
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={clean_key}"
    
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Error ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Connection Error: {str(e)}"

def get_elevenlabs_audio(text, api_key):
    url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key.strip(),
        # Anti-Ban Header: Pretends to be a real browser
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2", 
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.content
    else:
        return f"ElevenLabs Error: {response.text}"

# --- MAIN APP LOGIC ---

user_input = st.text_area("Ask me anything:", "Tell me a fun fact about robots.")

if st.button("Generate"):
    if not google_api_key or not elevenlabs_api_key:
        st.error("Please enter both API keys.")
    else:
        # 1. AUTO-DETECT MODEL
        with st.spinner("Finding best Google model..."):
            valid_model = find_working_gemini_model(google_api_key)
            
        if not valid_model:
            st.error("❌ Your API Key is valid, but Google says you have NO available models. Try creating a completely new API Key in a new project.")
        else:
            st.success(f"✅ Connected to: {valid_model}")
            
            # 2. GENERATE TEXT
            with st.spinner(f"Thinking using {valid_model}..."):
                ai_text = get_gemini_response(user_input, google_api_key, valid_model)
            
            if "Error" in ai_text:
                st.error(ai_text)
            else:
                st.write(ai_text)
                
                # 3. GENERATE VOICE
                with st.spinner("Synthesizing Voice..."):
                    audio_data = get_elevenlabs_audio(ai_text, elevenlabs_api_key)
                
                if isinstance(audio_data, bytes):
                    st.audio(audio_data, format="audio/mp3")
                    st.balloons()
                else:
                    st.error(audio_data)
                    st.info("⚠️ If you see 'Unusual Activity', ElevenLabs has banned the Cloud Server IP. YOU MUST RUN THIS LOCALLY (See instructions).")
