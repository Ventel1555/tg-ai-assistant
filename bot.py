import uuid
from dotenv import load_dotenv
import telebot
import os
import speech_recognition as sr
from pydub import AudioSegment
import io

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
language = os.getenv("LANGUAGE", "ru-RU") 

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    try:
        # Create temp filenames
        temp_dir = "temp_voice"
        os.makedirs(temp_dir, exist_ok=True)
        ogg_filename = f"{temp_dir}/{str(uuid.uuid4())}.ogg"
        wav_filename = f"{temp_dir}/{str(uuid.uuid4())}.wav"

        # Download the voice file
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Save as ogg file
        with open(ogg_filename, 'wb') as f:
            f.write(downloaded_file)

        # Convert ogg to wav using pydub
        audio = AudioSegment.from_ogg(ogg_filename)
        audio.export(wav_filename, format="wav")

        # Transcribe the audio to text
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_filename) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language=language)

        # Send the transcription back to the user
        bot.reply_to(message, f"Распознанный текст: {text}")

    except sr.UnknownValueError:
        bot.reply_to(message, "Не удалось распознать речь")
    except sr.RequestError as e:
        bot.reply_to(message, f"Ошибка сервиса распознавания: {e}")
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {str(e)}")
    finally:
        # Clean up temporary files
        if 'ogg_filename' in locals() and os.path.exists(ogg_filename):
            os.remove(ogg_filename)
        if 'wav_filename' in locals() and os.path.exists(wav_filename):
            os.remove(wav_filename)

bot.infinity_polling()