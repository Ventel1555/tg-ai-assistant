# TG AI Assistant

Voice bot Telegram assistant that uses AI to work with APIs of other applications

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/tg-ai-assistant.git
   cd tg-ai-assistant
   ```

2. Install required dependencies. Also check dependencies, if something dont work:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` with `.env.example` for BOT_TOKEN in @BotFather:

4. Change `docker-compose.yml`. Optional
without docker:
   ```bash
   sudo apt-get update 
   sudo apt-get install -y ffmpeg 
   sudo rm -rf /var/lib/apt/lists/*
   ```
## Model for spacy
   ```
   spacy download ru_core_news_sm
   ```
## Dependencies

- Python 3.12
- pydub
- python-dotenv
- aiogram
- spacy
- SpeechRecognition
- google-api-python-client
- google-auth-oauthlib
- google-auth