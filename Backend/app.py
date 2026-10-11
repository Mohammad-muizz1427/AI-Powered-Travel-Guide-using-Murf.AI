from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# After deploying the frontend, set FRONTEND_URL on Render
# (example: https://your-app.vercel.app). Until then it allows all origins.
FRONTEND_URL = os.getenv("FRONTEND_URL", "*")
CORS(app, origins=FRONTEND_URL)

api_key = os.getenv("API_GEMINI")
api_murfai = os.getenv("API_MURFAI")
client = genai.Client(api_key=api_key)

PROMPTS = {
    "Summary": """
You are a professional tourist guide.
Provide a high-level overview of "{place}" in {language}.

Focus on:
- The historical significance
- Why the place is famous
- Key architectural or cultural highlights

Keep the explanation concise, engaging, and easy to follow.
Avoid excessive details and dates.
Limit the response to around 200 words.

Respond ONLY in {language}.
""",

    "Detailed": """
You are a professional tourist guide.
Provide a detailed and immersive explanation of "{place}" in {language}.

Cover:
- Historical background and timeline
- Architectural design and unique features
- Cultural importance and notable events
- Interesting facts and visitor insights

Explain concepts clearly and in a storytelling manner.
Include relevant details and examples to create a rich experience.
Limit the response to around 400 words.

Respond ONLY in {language}.
"""
}


def generate_speech(text, voice_id, locale):
    """Returns MP3 bytes, or None if Murf fails."""
    url = "https://global.api.murf.ai/v1/speech/stream"
    headers = {
        "api-key": api_murfai,
        "Content-Type": "application/json"
    }
    data = {
        "voice_id": voice_id,
        "text": text,
        "locale": locale,
        "model": "FALCON",
        "format": "MP3",
        "sampleRate": 24000,
        "channelType": "MONO"
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=90)
    except requests.RequestException as e:
        print(f"Murf request error: {e}")
        return None

    if response.status_code != 200:
        print(f"Murf error {response.status_code}: {response.text[:300]}")
        return None

    return response.content


def generate_description(place, answer_type, language):
    prompt = PROMPTS[answer_type].format(place=place, language=language)
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",  # [Unverified] confirm this name in Google AI Studio
        contents=prompt
    )
    return response.text


@app.route("/")
def health():
    return {"status": "ok"}


@app.route("/generate-audio-guide", methods=["POST"])
def generate_audio_guide():
    data = request.get_json(silent=True) or {}

    place = data.get("place")
    answer_type = data.get("answerType")
    language = data.get("language")
    voice_id = data.get("voiceId")
    locale = data.get("locale")

    if not all([place, answer_type, language, voice_id, locale]):
        return jsonify({"error": "Missing required fields"}), 400

    if answer_type not in PROMPTS:
        return jsonify({"error": "Invalid answerType"}), 400

    try:
        text_description = generate_description(place, answer_type, language)
    except Exception as e:
        print(f"Gemini error: {e}")
        return jsonify({"error": "Text generation failed"}), 502

    audio_bytes = generate_speech(text_description, voice_id, locale)

    if audio_bytes is None:
        # Still send the text so the user sees something
        return jsonify({
            "description": text_description,
            "audioBase64": None,
            "error": "Speech generation failed"
        }), 200

    return jsonify({
        "description": text_description,
        "audioBase64": base64.b64encode(audio_bytes).decode("utf-8")
    })


if __name__ == "__main__":
    app.run(debug=False, port=5000)