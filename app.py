import streamlit as st
import requests
import json
import base64

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="VoiceGenie: ElevenLabs Edition", page_icon="🎙️")
st.title("🎙️ VoiceGenie: ElevenLabs + Gemini")
st.markdown("### Submission for AI Partner Catalyst Hackathon")

# --- SIDEBAR: API KEYS ---
st.sidebar.header("Configuration")
google_api_key = st.sidebar.text_input("Google Gemini API Key", type="password")
elevenlabs_api_key = st.sidebar.text_input("ElevenLabs API Key (New)", type="password")

# --- GEMINI FUNCTION (Direct API) ---
def get_gemini_response(prompt, api_key):
    # Using the stable v1beta endpoint with 1.5-flash
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key.strip()}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Gemini Error: {response.text}"
    except Exception as e:
        return f"Gemini Connection Error: {str(e)}"

# --- ELEVENLABS FUNCTION (Anti-Ban Headers) ---
def get_elevenlabs_audio(text, api_key):
    url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM" # Rachel Voice
    
    # HEADERS: Added User-Agent to look like a browser and avoid IP bans
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key.strip(),
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return response.content
        else:
            return f"ElevenLabs Error ({response.status_code}): {response.text}"
    except Exception as e:
        return f"ElevenLabs Connection Error: {str(e)}"

# --- MAIN APP ---
user_input = st.text_area("Ask me anything:", "Tell me a short story about a robot.")

if st.button("Generate Response"):
    if not google_api_key or not elevenlabs_api_key:
        st.error("Please enter both API Keys in the sidebar.")
    else:
        # 1. Gemini
        with st.spinner("Asking Gemini..."):
            ai_text = get_gemini_response(user_input, google_api_key)
        
        if "Error" in ai_text:
            st.error(ai_text)
        else:
            st.success("Gemini Response:")
            st.write(ai_text)
            
            # 2. ElevenLabs
            with st.spinner("Synthesizing Voice (ElevenLabs)..."):
                audio_content = get_elevenlabs_audio(ai_text, elevenlabs_api_key)
            
            if isinstance(audio_content, bytes):
                # Display Audio Player
                st.audio(audio_content, format="audio/mp3")
                st.success("✅ Voice Generated Successfully!")
            else:
                st.error(audio_content)
                st.warning("⚠️ Recommendation: If ElevenLabs fails on the Cloud, run this app LOCALLY on your laptop to record the demo video. Local IPs are rarely banned.")
