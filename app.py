import streamlit as st
import requests
import json

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="VoiceGenie", page_icon="🎙️")
st.title("🎙️ VoiceGenie: Direct Mode")
st.write("Using Direct REST API (Bypassing Python Libraries)")

# --- SIDEBAR: API KEYS ---
st.sidebar.header("Configuration")
google_api_key = st.sidebar.text_input("Google Gemini API Key", type="password")
elevenlabs_api_key = st.sidebar.text_input("ElevenLabs API Key", type="password")

# --- DIRECT API FUNCTIONS ---

def get_gemini_response_direct(prompt, api_key):
    """
    Sends a direct HTTP request to Google's API, bypassing the Python library.
    """
    if not api_key: return "Error: No API Key provided"
    
    # 1. clean the key
    key = api_key.strip()
    
    # 2. Define the endpoint (Using gemini-1.5-flash)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
    
    # 3. Define the payload
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        # 4. Check for success
        if response.status_code == 200:
            result = response.json()
            # Extract text from the complex JSON structure
            try:
                return result['candidates'][0]['content']['parts'][0]['text']
            except:
                return f"Error Parsing JSON: {result}"
        else:
            # If it fails, try the older model (Fallback)
            if "404" in str(response.status_code):
                return get_gemini_response_fallback(prompt, key)
            return f"Google API Error ({response.status_code}): {response.text}"
            
    except Exception as e:
        return f"Connection Error: {str(e)}"

def get_gemini_response_fallback(prompt, api_key):
    """Fallback to gemini-pro if flash fails"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        return f"Final Fallback Failed: {response.text}"

def text_to_speech(text, api_key):
    # VOICE ID: Rachel
    url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key.strip()
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

user_input = st.text_area("Ask me anything:", "Tell me a haiku about AI.")

if st.button("Generate Response"):
    if not google_api_key or not elevenlabs_api_key:
        st.error("❌ Please enter both API keys in the sidebar.")
    else:
        # 1. GEMINI (Direct HTTP)
        with st.spinner("Contacting Google Cloud (Direct)..."):
            ai_text = get_gemini_response_direct(user_input, google_api_key)
        
        if "Error" in ai_text and "Parsing" not in ai_text:
            st.error(ai_text)
            st.info("💡 If you see a 400 error, your API Key is invalid. If 404, the model is missing.")
        else:
            st.markdown("### 🤖 Gemini Answer:")
            st.write(ai_text)
            
            # 2. ELEVENLABS
            with st.spinner("Synthesizing Audio..."):
                audio_result = text_to_speech(ai_text, elevenlabs_api_key)
            
            if isinstance(audio_result, bytes):
                st.audio(audio_result, format="audio/mp3")
                st.success("✅ Success!")
            else:
                st.error(audio_result)
