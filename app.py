import streamlit as st
import google.generativeai as genai
import requests
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="VoiceGenie: Gemini + ElevenLabs", page_icon="🎙️")

st.title("🎙️ VoiceGenie: The Speaking AI")
st.markdown("### Powered by Google Cloud Gemini & ElevenLabs")

# --- SIDEBAR: API KEYS ---
st.sidebar.header("Configuration")
st.sidebar.info("Enter your API keys to start.")

google_api_key = st.sidebar.text_input("Google Gemini API Key", type="password")
elevenlabs_api_key = st.sidebar.text_input("ElevenLabs API Key", type="password")

# --- CORE FUNCTIONS ---

def get_gemini_response(prompt, api_key):
    try:
        genai.configure(api_key=api_key)
        # UPDATED: Changed to 'gemini-1.5-flash' (Newer, faster, works better)
        model = genai.GenerativeModel('gemini-1.5-flash') 
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error with Google Gemini: {str(e)}"

def text_to_speech(text, api_key):
    # UPDATED: Using a standard Voice ID (Rachel)
    url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM" 
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    data = {
        "text": text,
        # UPDATED: Changed to 'eleven_multilingual_v2' (Supported on Free Tier)
        "model_id": "eleven_multilingual_v2", 
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return response.content
        else:
            # Return the error text so we can see it in the app if it fails
            st.error(f"ElevenLabs Error: {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None

# --- MAIN APP LOGIC ---

user_input = st.text_area("What do you want to ask?", "Explain quantum physics in 2 sentences.")

if st.button("Generate & Speak"):
    if not google_api_key or not elevenlabs_api_key:
        st.warning("Please enter both API Keys in the sidebar!")
    else:
        with st.spinner("Consulting Google Gemini..."):
            # 1. Get Text from Gemini
            ai_text = get_gemini_response(user_input, google_api_key)
            
            # Check if Gemini actually returned text or an error
            if "Error with Google Gemini" in ai_text:
                st.error(ai_text)
            else:
                st.markdown("### 🤖 Gemini Says:")
                st.write(ai_text)

                with st.spinner("Synthesizing Voice with ElevenLabs..."):
                    # 2. Get Audio from ElevenLabs
                    audio_bytes = text_to_speech(ai_text, elevenlabs_api_key)
                    
                    if audio_bytes:
                        st.markdown("### 🔊 ElevenLabs Voice:")
                        st.audio(audio_bytes, format="audio/mp3")
                        st.success("Process Complete!")
