import asyncio, logging, os, sys, tempfile
from dotenv import load_dotenv
import speech_recognition as sr
from pydub import AudioSegment
from aiogram import F, Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from stt import process_text

load_dotenv()
# Инициализация проекта
BOT_TOKEN = os.getenv("BOT_TOKEN")
dp = Dispatcher()

# Обработчик команды /start
@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    await message.answer("Привет! Я бот для распознавания речи.")

@dp.message(F.voice)
async def handle_voice(message: types.Message, bot: Bot) -> None:
    with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as ogg_file, \
         tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as wav_file:
        
        ogg_path = ogg_file.name
        wav_path = wav_file.name

    try:
        voice_file = await bot.get_file(message.voice.file_id)
        file_path = voice_file.file_path
        
        await bot.download_file(file_path, destination=ogg_path)

        # Конвертируем OGG в WAV
        audio = AudioSegment.from_ogg(ogg_path)
        audio.export(wav_path, format="wav")

        # Распознавание речи
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            # Учитываем фоновый шум
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = recognizer.record(source)
            
            try:
                # Google Speech Recognition и SpaCy
                text = recognizer.recognize_google(audio_data, language="ru-RU")
                
                # Извлекаем намерение
                result = process_text(text)  # Новая функция из stt.py
                
                if result["intent"] == "create_reminder":
                    params = result["parameters"]
                    response = f"✅ Создаю напоминание: {params['title'] or 'Без названия'} в {params['datetime'] or 'не указано'}"
                    await message.reply(response)
                else:
                    await message.reply("🤔 Не понял, уточните, пожалуйста")

                await message.reply(f"Распознанный текст:\n\n{text}")
            except sr.UnknownValueError:
                await message.reply("Не удалось распознать речь. Попробуйте записать сообщение в более тихом месте.")
            except sr.RequestError as e:
                await message.reply(f"Ошибка сервиса распознавания: {e}")
            except Exception as e:
                await message.reply(f"Произошла непредвиденная ошибка: {e}")

    except Exception as e:
        logging.error(f"Ошибка при обработке голосового сообщения: {e}")
        await message.reply("Произошла ошибка при обработке голосового сообщения.")
    
    finally:
        for file_path in [ogg_path, wav_path]:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logging.error(f"Ошибка при удалении файла {file_path}: {e}")

# @dp.message(F.text)
# async def handle_text(message: types.Message) -> None:
#     await message.answer("Отправьте мне голосовое сообщение для распознавания текста.")

# Запуск бота
async def main() -> None:

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
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