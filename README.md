# Voice to Text Telegram Bot

A Telegram bot that converts voice messages to text using AI-powered speech recognition.

## Features
- Converts voice messages to text in Russian (`ru-RU`) using Google Speech Recognition.
- Handles errors gracefully and provides user feedback.
- Supports Docker for easy deployment.

## Prerequisites
- **Python 3.12** or higher
- Telegram bot token from [BotFather](https://t.me/BotFather)
- [ffmpeg](https://ffmpeg.org) for audio processing

## Setup
1. Create a `.env` file with your bot token:
   ```bash
   echo "BOT_TOKEN=your_bot_token_here" > .env
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the bot:
   ```bash
   python voicetotext.py
   ```

## Docker Setup
1. Build and run with Docker Compose:
   ```bash
   docker-compose up --build
   ```

## Dependencies
- `aiogram`: Telegram Bot API framework
- `pydub`: Audio file processing
- `python-dotenv`: Environment variable management
- `SpeechRecognition`: Speech-to-text conversion

## Project Structure
```
tg-ai-assistant/
├── voicetotext.py          # Bot
├── .env                    # Environment variables
├── .gitignore              # Git ignore file
├── requirements.txt        # Dependencies
├── README.md               # Documentation
├── Dockerfile              # Docker configuration
└──docker-compose.yml       # Docker Compose configuration
```