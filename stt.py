# stt.py
# Этот модуль обрабатывает текст голосовых сообщений, используя spaCy для обработки естественного языка на русском языке.
# Он извлекает намерение (создание или удаление события) и подробности (название события, дата, время).
# Интегрируется с API Google Календаря для создания или удаления событий.
# Для аутентификации реализует поток OAuth2 для каждого пользователя с Google.
# Предполагается, что у вас есть бот Telegram, настроенный в voicetotext.py с использованием aiogram.
# Также загрузите credentials.json из Google Cloud Console (идентификаторы клиентов OAuth 2.0, тип веб-приложения).
# Установите redirect_uri на ваш сервер, например, https://yourdomain.com/oauth_callback (используйте ngrok для локального тестирования).
# Сохраните credentials.json в корне проекта.
# Для хранения используйте pickle для сохранения токенов каждого пользователя.
from dotenv import load_dotenv
import spacy
import datetime
import pickle
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from aiogram import Bot  # Assume Bot instance is passed or imported from main

load_dotenv()
# Инициализация проекта
BOT_TOKEN = os.getenv("BOT_TOKEN")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# Load spaCy model for Russian
nlp = spacy.load("ru_core_news_sm")

# Path to token storage
TOKEN_FILE = 'tokens.pickle'

# Google API scopes for Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Your bot token from .env or main
# Assume BOT = Bot(token=...) is defined in main and passed if needed

def load_tokens():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token_file:
            return pickle.load(token_file)
    return {}

def save_tokens(tokens):
    with open(TOKEN_FILE, 'wb') as token_file:
        pickle.dump(tokens, token_file)

def get_credentials(user_id):
    tokens = load_tokens()
    if str(user_id) in tokens:
        creds = Credentials.from_authorized_user_info(tokens[str(user_id)], SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            tokens[str(user_id)] = creds.to_json()
            save_tokens(tokens)
        return creds
    return None

# Function to generate auth URL for user
def generate_auth_url(user_id, redirect_uri):
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    flow.redirect_uri = redirect_uri
    auth_url, state = flow.authorization_url(prompt='consent', state=str(user_id))
    return auth_url

# This function should be called in your OAuth callback endpoint (e.g., in FastAPI or aiohttp server)
# Assume you set up a web server to handle /oauth_callback?code=...&state=...
async def handle_oauth_callback(code, state, bot: Bot):
    user_id = int(state)
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    flow.redirect_uri = REDIRECT_URI
    creds = flow.fetch_token(code=code)
    tokens = load_tokens()
    tokens[str(user_id)] = creds  # Store as dict or json
    save_tokens(tokens)
    # Send message to user
    await bot.send_message(user_id, "Авторизация в Google Calendar прошла успешно! Теперь вы можете создавать и удалять напоминания.")

# Main function to process text from voice message
async def process_text(text: str, user_id: int, bot: Bot, redirect_uri: str = 'your_redirect_uri_here'):
    # Use spaCy to process text
    doc = nlp(text.lower())

    # Extract entities
    event_name = None
    date = None
    time = None
    for ent in doc.ents:
        if ent.label_ == 'DATE':
            date = ent.text
        elif ent.label_ == 'TIME':
            time = ent.text
        else:
            # Assume other text as event name
            if not event_name:
                event_name = ent.text

    # Fallback for event name if no specific entity
    if not event_name:
        event_name = ' '.join([token.text for token in doc if not token.is_stop and token.pos_ not in ['PUNCT', 'SPACE']])

    # Determine intent
    intent = None
    if any(word in text.lower() for word in ['создай', 'добавь', 'напомни', 'запись', 'событие']):
        intent = 'create'
    elif any(word in text.lower() for word in ['удали', 'отмени', 'убери']):
        intent = 'delete'

    if not intent:
        return "Не удалось определить действие. Пожалуйста, укажите 'создай' или 'удали'."

    # Parse date and time (simple parsing, you can improve with dateparser library: pip install dateparser)
    try:
        if date:
            parsed_date = datetime.datetime.strptime(date, '%d %B %Y')  # Example format, adjust as needed
        else:
            parsed_date = datetime.datetime.now() + datetime.timedelta(days=1)  # Default tomorrow
        if time:
            parsed_time = datetime.datetime.strptime(time, '%H:%M').time()
            start_datetime = datetime.datetime.combine(parsed_date.date(), parsed_time)
        else:
            start_datetime = parsed_date.replace(hour=9, minute=0)  # Default 9:00
        end_datetime = start_datetime + datetime.timedelta(hours=1)  # Default 1 hour event
    except ValueError:
        return "Не удалось разобрать дату или время. Пожалуйста, укажите четко, например 'завтра в 15:00'."

    # Get credentials
    creds = get_credentials(user_id)
    if not creds:
        auth_url = generate_auth_url(user_id, redirect_uri)
        await bot.send_message(user_id, f"Пожалуйста, авторизуйтесь в Google: {auth_url}")
        return "Авторизация требуется."

    # Build Google Calendar service
    service = build('calendar', 'v3', credentials=creds)

    if intent == 'create':
        event = {
            'summary': event_name,
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'UTC',  # Adjust timezone
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'UTC',
            },
        }
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        return f"Событие '{event_name}' создано: {created_event.get('htmlLink')}"

    elif intent == 'delete':
        # For delete, need to find event by summary or time
        # Simple: list events and find matching
        events_result = service.events().list(calendarId='primary', timeMin=start_datetime.isoformat() + 'Z',
                                              maxResults=10, singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])
        for event in events:
            if event['summary'].lower() == event_name.lower():
                service.events().delete(calendarId='primary', eventId=event['id']).execute()
                return f"Событие '{event_name}' удалено."
        return "Событие не найдено."