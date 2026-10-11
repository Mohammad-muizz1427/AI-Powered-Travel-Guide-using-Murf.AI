# AI Powered Travel Guide using Murf.AI

An AI audio travel guide for famous places in India. Pick a destination, choose a language and a voice, and the app writes a short guide with Google Gemini and reads it out loud using Murf.AI.

**Live backend:** https://ai-powered-travel-guide-using-murf-ai.onrender.com/
**Live app:** _add your Vercel link here_

## Features

- Six destinations: Taj Mahal, Red Fort, Gateway of India, Hawa Mahal, Golden Temple and Mysore Palace
- Four languages: English, Hindi, Tamil and Telugu
- Male or female voice
- Two guide lengths: **Summary** (about 200 words) and **Detailed** (about 400 words)
- Audio player with a text transcript you can open and close

## How it works

1. You choose a place, language, voice and guide length in the browser.
2. The frontend sends a request to the Flask backend.
3. The backend asks Gemini to write the guide in the chosen language.
4. The backend sends that text to Murf.AI to turn it into speech (MP3).
5. The backend returns the text and the audio (base64) to the browser, which plays it.

## Tech stack

| Part | Tools |
|------|-------|
| Frontend | HTML, JavaScript, Tailwind CSS (CDN) |
| Backend | Python, Flask, Flask-CORS, Gunicorn |
| AI text | Google Gemini (`google-genai`) |
| AI voice | Murf.AI speech API |
| Hosting | Vercel (frontend), Render (backend) |

## Project structure

```
.
├── Backend/
│   ├── app.py              # Flask API
│   └── requirements.txt    # Python packages
├── Frontend/
│   ├── index.html          # Page layout
│   └── index.js            # App logic
└── .gitignore
```

## Run it locally

You need Python 3 and API keys for Gemini and Murf.AI.

**1. Clone the repo**

```bash
git clone https://github.com/Mohammad-muizz1427/AI-Powered-Travel-Guide-using-Murf.AI.git
cd AI-Powered-Travel-Guide-using-Murf.AI
```

**2. Set up the backend**

```bash
cd Backend
python -m venv .venv
```

Activate the virtual environment:

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

Install the packages:

```bash
pip install -r requirements.txt
```

**3. Add your API keys**

Create a file named `Backend/.env`:

```
API_GEMINI=your_gemini_api_key
API_MURFAI=your_murf_api_key
```

Never commit this file. It is already listed in `.gitignore`.

**4. Start the backend**

```bash
python app.py
```

The API runs at `http://127.0.0.1:5000`.

**5. Point the frontend to your local backend**

In `Frontend/index.js`, set:

```js
const GENERATE_AUDIO_GUIDE_API_URL = "http://127.0.0.1:5000/generate-audio-guide";
```

**6. Open the frontend**

Open `Frontend/index.html` in your browser (or use the VS Code Live Server extension).

## API

### `GET /`

Health check. Returns `{"status": "ok"}`.

### `POST /generate-audio-guide`

Request body (JSON):

| Field | Description | Example |
|-------|-------------|---------|
| `place` | Name of the place | `"Taj Mahal"` |
| `answerType` | `"Summary"` or `"Detailed"` | `"Summary"` |
| `language` | Language of the guide | `"Hindi"` |
| `voiceId` | Murf voice ID | `"Aman"` |
| `locale` | Murf locale | `"hi-IN"` |

Response (JSON):

```json
{
  "description": "Text of the guide...",
  "audioBase64": "base64 encoded MP3..."
}
```

If speech generation fails, `audioBase64` is `null` and the text is still returned. Missing or invalid fields return a `400` error.

## Deployment

### Backend on Render

1. Create a new **Web Service** and connect your GitHub repo.
2. Set these values:
   - **Root Directory:** `Backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --timeout 120`
3. Add environment variables:
   - `API_GEMINI`: your Gemini key
   - `API_MURFAI`: your Murf key
   - `FRONTEND_URL`: your Vercel link, with no `/` at the end (this limits CORS to your site)

### Frontend on Vercel

1. Import the same repo as a new project.
2. Set **Root Directory** to `Frontend`.
3. Set **Framework Preset** to **Other** and leave the build settings empty.
4. Deploy.

Before deploying, make sure `GENERATE_AUDIO_GUIDE_API_URL` in `Frontend/index.js` points to your Render URL:

```js
const GENERATE_AUDIO_GUIDE_API_URL = "https://ai-powered-travel-guide-using-murf-ai.onrender.com/generate-audio-guide";
```

## Troubleshooting

- **First request is slow:** the free Render instance may be asleep. Wait a minute and try again.
- **CORS error in the browser console:** `FRONTEND_URL` on Render must match your Vercel link exactly.
- **Text shows but there is no audio:** check the Render logs. The backend prints the exact Murf error, which often points to a wrong voice ID.
- **"Generation failed" alert:** check the Render logs for the Gemini or Murf error message.

## Security notes

- Keep API keys only in environment variables, never in the repo.
- If a key was ever committed, delete it and create a new one.

## Author

Mohammad ([@Mohammad-muizz1427](https://github.com/Mohammad-muizz1427))
