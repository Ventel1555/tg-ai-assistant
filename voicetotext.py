import asyncio
import logging
import os
import sys
import tempfile
import sqlite3
import uuid
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import speech_recognition as sr
from pydub import AudioSegment
from aiogram import F, Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import caldav
from caldav.elements import dav, cdav
from icalendar import Calendar, Event, Alarm
import dateparser
from urllib.parse import quote
import html
import requests  # Добавлено для настройки useUnsafeHeaderParsing

# Включаем отладку для caldav
logging.getLogger('caldav').setLevel(logging.DEBUG)

# Настройка useUnsafeHeaderParsing для requests (для некорректных заголовков)
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[400, 429, 500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))
# Включаем unsafe header parsing
from urllib3 import PoolManager
PoolManager.DEFAULT_HEADERS['User-Agent'] = 'python-caldav/2.0.1'
caldav.lib.vcal.requests_session = session  # Подменяем сессию в caldav

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            email TEXT,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class AuthForm(StatesGroup):
    email = State()
    password = State()

@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    await message.answer("Привет! Я бот для работы с напоминаниями в Mail.ru Календаре.\n"
                         "Сначала авторизуйся: /auth\n"
                         "Затем отправь голосовое или текст: 'напомни [описание] [дата] [время]' или 'удали напоминание [описание]'")

@dp.message(Command("auth"))
async def start_auth(message: types.Message, state: FSMContext):
    await state.set_state(AuthForm.email)
    await message.reply("Введите ваш email Mail.ru (например, example@mail.ru)")

@dp.message(AuthForm.email)
async def process_email(message: types.Message, state: FSMContext):
    email = message.text.strip()
    if "@mail.ru" not in email.lower():
        await message.reply("Неверный email. Должен быть @mail.ru. Попробуйте снова.")
        return
    await state.update_data(email=email)
    await state.set_state(AuthForm.password)
    await message.reply("Введите пароль приложения (создайте в Mail.ru: Настройки > Безопасность > Пароли для внешних приложений).")

@dp.message(AuthForm.password)
async def process_password(message: types.Message, state: FSMContext):
    data = await state.get_data()
    email = data['email']
    password = message.text.strip()
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO users (user_id, email, password) VALUES (?, ?, ?)',
              (message.from_user.id, email, password))
    conn.commit()
    conn.close()
    
    await state.clear()
    await message.reply("Авторизация завершена! Проверяем подключение...")
    
    success = False
    urls_to_try = [
        "https://calendar.mail.ru/dav/",  # Новый базовый URL
        f"https://calendar.mail.ru/principals/users/{quote(email)}/",
    ]
    
    for url in urls_to_try:
        try:
            client = caldav.DAVClient(url=url, username=email, password=password, timeout=10)
            principal = client.principal()
            calendars = principal.calendars()
            if calendars:
                await message.reply(f"Подключение успешно через {url}! Найдено календарей: {len(calendars)}.")
                success = True
                break
            else:
                raise Exception("Календари не найдены")
        except caldav.lib.error.PropfindError as e:
            logging.error(f"PropfindError для {url}: {e}")
            error_msg = f"Ошибка CalDAV для {url}: {html.escape(str(e))}. "
            if "400" in str(e):
                error_msg += "Возможно, неверный URL или учетные данные."
            continue
        except Exception as e:
            logging.error(f"Ошибка для {url}: {e}")
            error_msg = f"Ошибка подключения к {url}: {html.escape(str(e))}. "
            if "timeout" in str(e).lower():
                error_msg += "Проверьте интернет или попробуйте позже."
            continue
    
    if not success:
        await message.reply(error_msg + "Не удалось подключиться. Проверьте email/пароль, создайте календарь в https://calendar.mail.ru/ и попробуйте /auth заново.")

async def create_reminder(user_id: int, summary: str, date_str: str, time_str: str) -> str:
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT email, password FROM users WHERE user_id = ?', (user_id,))
    res = c.fetchone()
    conn.close()
    
    if not res:
        return "Вы не авторизованы. Используйте /auth"
    
    email, password = res
    base_url = "https://calendar.mail.ru/dav/"  # Новый URL
    
    max_retries = 2
    urls_to_try = [
        base_url,
        f"https://calendar.mail.ru/principals/users/{quote(email)}/",
    ]
    
    for attempt in range(max_retries + 1):
        for url in urls_to_try:
            try:
                client = caldav.DAVClient(url=url, username=email, password=password, timeout=10)
                principal = client.principal()
                calendars = principal.calendars()
                if not calendars:
                    raise Exception("Календари не найдены")
                
                calendar = calendars[0]
                
                dt_str = f"{date_str} {time_str}" if time_str else date_str
                dtstart = dateparser.parse(dt_str, languages=['ru'])
                if not dtstart:
                    return "Не удалось распознать дату/время. Пример: 'завтра 10:00'"
                dtstart = dtstart.replace(tzinfo=None)
                
                cal = Calendar()
                event = Event()
                event.add('summary', summary)
                event.add('dtstart', dtstart)
                event.add('dtend', dtstart + timedelta(hours=1))
                event.add('uid', str(uuid.uuid4()))
                
                alarm = Alarm()
                alarm.add("action", "DISPLAY")
                alarm.add('description', summary)
                alarm.add("trigger", timedelta(minutes=-15))
                event.add_component(alarm)
                
                cal.add_component(event)
                
                calendar.add_event(cal.to_ical())
                return f"Напоминание '{summary}' создано на {dtstart.strftime('%d.%m.%Y %H:%M')}"
            
            except caldav.lib.error.PropfindError as e:
                logging.error(f"PropfindError (попытка {attempt + 1}, {url}): {e}")
                if attempt < max_retries:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return f"Ошибка CalDAV (PropfindError для {url}). Проверьте email/пароль или создайте календарь."
            except Exception as e:
                logging.error(f"Ошибка создания (попытка {attempt + 1}, {url}): {e}")
                if "timeout" in str(e).lower() or "connect" in str(e).lower():
                    if attempt < max_retries:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    return "Timeout при подключении к Mail.ru. Проверьте интернет или попробуйте позже."
                if attempt < max_retries:
                    await asyncio.sleep(2 ** attempt)
                    continue
                safe_error = html.escape(str(e))
                return f"Ошибка: {safe_error}. Проверьте credentials."

async def delete_reminder(user_id: int, summary: str) -> str:
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT email, password FROM users WHERE user_id = ?', (user_id,))
    res = c.fetchone()
    conn.close()
    
    if not res:
        return "Вы не авторизованы. Используйте /auth"
    
    email, password = res
    base_url = "https://calendar.mail.ru/dav/"
    
    max_retries = 2
    urls_to_try = [
        base_url,
        f"https://calendar.mail.ru/principals/users/{quote(email)}/",
    ]
    
    for attempt in range(max_retries + 1):
        for url in urls_to_try:
            try:
                client = caldav.DAVClient(url=url, username=email, password=password, timeout=10)
                principal = client.principal()
                calendars = principal.calendars()
                if not calendars:
                    raise Exception("Календари не найдены")
                
                calendar = calendars[0]
                
                events = calendar.events()
                found = False
                for event in events:
                    event_summary = event.vobject_instance.vevent.summary.value.lower()
                    if summary.lower() in event_summary:
                        event.delete()
                        found = True
                        break
                
                if found:
                    return f"Напоминание с '{summary}' удалено."
                else:
                    return "Напоминание не найдено."
            
            except Exception as e:
                logging.error(f"Ошибка удаления (попытка {attempt + 1}, {url}): {e}")
                if attempt < max_retries:
                    await asyncio.sleep(2 ** attempt)
                    continue
                safe_error = html.escape(str(e))
                return f"Ошибка: {safe_error}"

async def process_text(text: str, user_id: int) -> str:
    text_lower = text.lower()
    if "напомни" in text_lower:
        parts = text.split()[1:]
        if len(parts) < 3:
            return "Формат: 'напомни [описание] [дата] [время]'. Пример: 'напомни купить молоко завтра 10:00'"
        
        time_str = parts[-1] if ":" in parts[-1] else ""
        date_str = parts[-2] if time_str else parts[-1]
        summary = " ".join(parts[:-2 if time_str else -1])
        
        return await create_reminder(user_id, summary, date_str, time_str)
    
    elif "удали напоминание" in text_lower:
        summary = " ".join(text.split()[2:])
        if not summary:
            return "Укажите описание для удаления."
        return await delete_reminder(user_id, summary)
    
    else:
        return "Неизвестная команда. Используйте 'напомни...' или 'удали напоминание...'"

@dp.message(F.voice)
async def handle_voice(message: types.Message, bot: Bot) -> None:
    ogg_path = None
    wav_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as ogg_file, \
             tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as wav_file:
            ogg_path = ogg_file.name
            wav_path = wav_file.name

        voice_file = await bot.get_file(message.voice.file_id)
        await bot.download_file(voice_file.file_path, ogg_path)

        audio = AudioSegment.from_ogg(ogg_path)
        audio.export(wav_path, format="wav")

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = recognizer.record(source)
            
            text = recognizer.recognize_google(audio_data, language="ru-RU")
            await message.reply(f"Распознано: {text}")
            
            result = await process_text(text, message.from_user.id)
            await message.reply(result)

    except sr.UnknownValueError:
        await message.reply("Не удалось распознать речь. Попробуйте в тихом месте.")
    except sr.RequestError as e:
        safe_e = html.escape(str(e))
        await message.reply(f"Ошибка сервиса: {safe_e}")
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        safe_e = "Произошла непредвиденная ошибка" if '<' in str(e) else html.escape(str(e))
        await message.reply(f"Ошибка: {safe_e}")
    
    finally:
        for file_path in [ogg_path, wav_path]:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    logging.error(f"Ошибка удаления {file_path}: {e}")

@dp.message(F.text)
async def handle_text(message: types.Message) -> None:
    text = message.text
    result = await process_text(text, message.from_user.id)
    await message.answer(result if result else "Отправьте голосовое или команду для напоминания.")

async def main() -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout
    )
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен")