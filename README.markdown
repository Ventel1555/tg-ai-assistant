# TG AI Assistant

A Telegram voice bot that uses AI to process voice messages and interact with the Google Calendar API to create or delete events. The bot leverages `spaCy` for natural language processing and `SpeechRecognition` for voice-to-text transcription.

## Prerequisites

- **Python 3.12** or higher
- Telegram bot token from [BotFather](https://t.me/BotFather)
- Google Cloud project with Google Calendar API enabled and `credentials.json`
- [ngrok](https://ngrok.com) account (free or paid)
- [ffmpeg](https://ffmpeg.org) for audio processing

## Installation and Setup

Detailed setup instructions are available in:
- [English Instructions](./instructions.md)
- [Русские инструкции](./instructions-ru.md)
- [Google Cloud Console Setup (на русском)](./google_cloud_setup.md)

### Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/tg-ai-assistant.git
   cd tg-ai-assistant
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   python -m spacy download ru_core_news_sm
   ```

3. Configure `.env` with your bot token and ngrok URL.

4. Set up ngrok and Google Cloud Console (see linked instructions).

5. Run the FastAPI server and bot:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000
   python voicetotext.py
   ```

## Dependencies

- `pydub`
- `python-dotenv`
- `aiogram`
- `spacy`
- `SpeechRecognition`
- `google-api-python-client`
- `google-auth-oauthlib`
- `google-auth`
- `fastapi`
- `uvicorn`

## Notes for Users in Russia

Due to potential IP restrictions, you may need a VPN (e.g., ProtonVPN) to use ngrok reliably. See [instructions-ru.md](./instructions-ru.md) for troubleshooting tips.

## License
