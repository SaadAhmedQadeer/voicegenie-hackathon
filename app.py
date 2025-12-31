import streamlit as st
import google.generativeai as genai
import requests

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="VoiceGenie Debug", page_icon="🛠️")

st.title("🛠️ VoiceGenie: Debug Mode")
st.warning("This mode will show the exact error from Google if it fails.")

# --- SIDEBAR: API KEYS ---
st.sidebar.header("Configuration")
google_api_key = st.sidebar.text_input("Google Gemini API Key", type="password")
elevenlabs_api_key = st.sidebar.text_input("ElevenLabs API Key", type="password")

# --- FUNCTIONS ---

def test_gemini_connection(prompt, api_key):
    # Strip any accidental spaces from the key
    clean_key = api_key.strip()
    
    try:
        genai.configure(api_key=clean_key)
        
        # We use the most standard model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # specific call to catch authentication errors
        response = model.generate_content(prompt)
        return True, response.text
    except Exception as e:
        # Return the RAW error message
        return False, str(e)

def text_to_speech(text, api_key):
    clean_key = api_key.strip()
    url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": clean_key
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2", 
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return response.content
        else:
            return f"ElevenLabs Error: {response.text}"
    except Exception as e:
        return f"Connection Error: {str(e)}"

# --- MAIN APP LOGIC ---

user_input = st.text_area("Ask me anything:", "Hello, are you working?")

if st.button("Test Connection"):
    if not google_api_key or not elevenlabs_api_key:
        st.error("❌ Please enter both API keys.")
    else:
        # 1. TEST GEMINI
        with st.spinner("Testing Google Key..."):
            success, result = test_gemini_connection(user_input, google_api_key)
        
        if not success:
            st.error("❌ Google Gemini Failed!")
            st.code(result, language="text") # This prints the EXACT error
            st.info("💡 If the error says '403' or 'INVALID_ARGUMENT', your API Key is wrong.")
        else:
            st.success("✅ Google Gemini Connected!")
            st.write(result)
            
            # 2. TEST ELEVENLABS
            with st.spinner("Testing ElevenLabs Key..."):
                audio_result = text_to_speech(result, elevenlabs_api_key)
            
            if isinstance(audio_result, bytes):
                st.audio(audio_result, format="audio/mp3")
                st.success("✅ ElevenLabs Connected!")
            else:
                st.error("❌ ElevenLabs Failed")
                st.write(audio_result)
