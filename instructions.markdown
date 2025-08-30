# Instructions for Setting Up TG AI Assistant

This document provides detailed steps to set up and run the **TG AI Assistant** Telegram voice bot, which integrates with Google Calendar API to create and delete events. The instructions are tailored for local development, with specific guidance for users in Russia facing IP-related restrictions.

## Prerequisites

- **Python 3.12** or higher
- A Telegram bot token from [BotFather](https://t.me/BotFather)
- A Google Cloud project with Google Calendar API enabled and `credentials.json`
- [ngrok](https://ngrok.com) account (free or paid) for OAuth callback
- [ffmpeg](https://ffmpeg.org) for audio processing
- A working internet connection (VPN recommended for Russia)

## Step 1: Clone the Repository

Clone the project repository and navigate to the project directory:
```bash
git clone https://github.com/yourusername/tg-ai-assistant.git
cd tg-ai-assistant
```

## Step 2: Set Up Virtual Environment

Create and activate a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate
```

## Step 3: Install Dependencies

Install required Python packages:
```bash
pip install -r requirements.txt
```
If `requirements.txt` is missing, install manually:
```bash
pip install pydub python-dotenv aiogram spacy SpeechRecognition google-api-python-client google-auth-oauthlib google-auth fastapi uvicorn
```

Install the spaCy model for Russian:
```bash
python -m spacy download ru_core_news_sm
```

## Step 4: Install ffmpeg

`ffmpeg` is required to convert Telegram's OGG audio files to WAV for speech recognition.

- **Linux (Ubuntu/Debian)**:
  ```bash
  sudo apt-get update
  sudo apt-get install -y ffmpeg
  sudo rm -rf /var/lib/apt/lists/*
  ```
- **Windows**:
  Download `ffmpeg` from [ffmpeg.org](https://ffmpeg.org/download.html), extract it, and add the `bin` folder to your system PATH.
- **macOS**:
  ```bash
  brew install ffmpeg
  ```

## Step 5: Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` with your Telegram bot token and ngrok URL:
   ```plaintext
   BOT_TOKEN=your-telegram-bot-token
   REDIRECT_URI=https://your-ngrok-domain.ngrok-free.app/oauth_callback
   ```
   - Replace `your-telegram-bot-token` with the token from BotFather.
   - Replace `your-ngrok-domain` with the ngrok URL obtained in Step 6.

## Step 6: Set Up ngrok

ngrok creates a public URL for your local FastAPI server to handle Google OAuth callbacks.

1. **Download and Install ngrok**:
   - Download from [ngrok.com](https://ngrok.com/download).
   - For **Linux**:
     ```bash
     unzip ngrok-stable-linux-amd64.zip
     mv ngrok /usr/local/bin/ngrok
     chmod +x /usr/local/bin/ngrok
     ```
   - For **Windows**:
     Extract `ngrok.exe` to a folder (e.g., `C:\ngrok`) and add it to PATH.

2. **Authenticate ngrok**:
   - Sign up at [ngrok.com](https://ngrok.com) and get your authtoken from [dashboard.ngrok.com](https://dashboard.ngrok.com/get-started/your-authtoken).
   - Run:
     ```bash
     ngrok authtoken <your-auth-token>
     ```

3. **Start ngrok**:
   Expose port 8000 (used by FastAPI):
   ```bash
   ngrok http 8000
   ```
   Copy the generated URL (e.g., `https://abc123.ngrok-free.app`).

## Step 7: Configure Google Cloud Console

Set up Google Cloud Console for OAuth 2.0 authentication. Follow the detailed steps in [google_cloud_setup.md](./google_cloud_setup.md) to:
- Create a project (e.g., `TelegramBotCalendar`).
- Enable Google Calendar API.
- Configure OAuth Consent Screen with the scope `https://www.googleapis.com/auth/calendar`.
- Create an OAuth 2.0 Client ID for a **Web application**.
- Add the ngrok URL as an **Authorized redirect URI** (e.g., `https://abc123.ngrok-free.app/oauth_callback`).
- Download `credentials.json` and place it in the project root.

## Step 8: Run the Project

1. **Start the FastAPI server** (handles OAuth callbacks):
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000
   ```

2. **Start the Telegram bot**:
   ```bash
   python voicetotext.py
   ```

3. **Keep ngrok running**:
   Ensure the ngrok tunnel is active in a separate terminal.
