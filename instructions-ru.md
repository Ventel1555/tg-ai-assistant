# Инструкции по настройке TG AI Assistant (на русском)

Этот документ содержит подробные шаги по настройке и запуску Telegram-бота **TG AI Assistant**, который обрабатывает голосовые сообщения и взаимодействует с Google Calendar API для создания и удаления событий. Инструкции адаптированы для локальной разработки, с учетом возможных ограничений для пользователей в России из-за IP-блокировок.

## Требования

- **Python 3.12** или выше
- Токен Telegram-бота от [BotFather](https://t.me/BotFather)
- Проект в Google Cloud с включенным Google Calendar API и файлом `credentials.json`
- Аккаунт [ngrok](https://ngrok.com) (бесплатный или платный) для обработки OAuth callback
- [ffmpeg](https://ffmpeg.org) для обработки аудиофайлов
- Стабильное интернет-соединение (рекомендуется VPN для России)

## Шаг 1: Клонирование репозитория

Склонируйте репозиторий и перейдите в папку проекта:
```bash
git clone https://github.com/yourusername/tg-ai-assistant.git
cd tg-ai-assistant
```

## Шаг 2: Настройка виртуального окружения

Создайте и активируйте виртуальное окружение Python:
```bash
python -m venv venv
source venv/bin/activate  # Для Windows: venv\Scripts\activate
```

## Шаг 3: Установка зависимостей

Установите необходимые Python-пакеты:
```bash
pip install -r requirements.txt
```
Если файл `requirements.txt` отсутствует, установите пакеты вручную:
```bash
pip install pydub python-dotenv aiogram spacy SpeechRecognition google-api-python-client google-auth-oauthlib google-auth fastapi uvicorn
```

Установите модель spaCy для русского языка:
```bash
python -m spacy download ru_core_news_sm
```

## Шаг 4: Установка ffmpeg

`ffmpeg` необходим для конвертации OGG-аудиофайлов Telegram в WAV для распознавания речи.

- **Linux (Ubuntu/Debian)**:
  ```bash
  sudo apt-get update
  sudo apt-get install -y ffmpeg
  sudo rm -rf /var/lib/apt/lists/*
  ```
- **Windows**:
  Скачайте `ffmpeg` с [ffmpeg.org](https://ffmpeg.org/download.html), распакуйте и добавьте папку `bin` в PATH системы.
- **macOS**:
  ```bash
  brew install ffmpeg
  ```

## Шаг 5: Настройка переменных окружения

1. Скопируйте пример файла окружения:
   ```bash
   cp .env.example .env
   ```
2. Отредактируйте `.env`, указав токен бота и URL ngrok:
   ```plaintext
   BOT_TOKEN=your-telegram-bot-token
   REDIRECT_URI=https://your-ngrok-domain.ngrok-free.app/oauth_callback
   ```
   - Замените `your-telegram-bot-token` на токен от BotFather.
   - Замените `your-ngrok-domain` на URL ngrok, который вы получите на следующем шаге.

## Шаг 6: Настройка ngrok

ngrok создаёт публичный URL для вашего локального FastAPI-сервера, чтобы обрабатывать OAuth callback от Google.

1. **Скачайте и установите ngrok**:
   - Скачайте с [ngrok.com](https://ngrok.com/download).
   - Для **Linux**:
     ```bash
     unzip ngrok-stable-linux-amd64.zip
     mv ngrok /usr/local/bin/ngrok
     chmod +x /usr/local/bin/ngrok
     ```
   - Для **Windows**:
     Распакуйте `ngrok.exe` в папку (например, `C:\ngrok`) и добавьте её в PATH.

2. **Аутентификация ngrok**:
   - Зарегистрируйтесь на [ngrok.com](https://ngrok.com) и получите authtoken на [dashboard.ngrok.com](https://dashboard.ngrok.com/get-started/your-authtoken).
   - Выполните:
     ```bash
     ngrok authtoken <your-auth-token>
     ```

3. **Запустите ngrok**:
   Пробросьте порт 8000 (используется FastAPI):
   ```bash
   ngrok http 8000
   ```
   Скопируйте сгенерированный URL (например, `https://abc123.ngrok-free.app`).

## Шаг 7: Настройка Google Cloud Console

Настройте Google Cloud Console для аутентификации OAuth 2.0. Подробные шаги описаны в [google_cloud_setup.md](./google_cloud_setup.md). Основные действия:
- Создайте проект (например, `TelegramBotCalendar`).
- Включите Google Calendar API.
- Настройте OAuth Consent Screen с областью доступа `https://www.googleapis.com/auth/calendar`.
- Создайте OAuth 2.0 Client ID для **Web application**.
- Добавьте ngrok URL в **Authorized redirect URIs** (например, `https://abc123.ngrok-free.app/oauth_callback`).
- Скачайте `credentials.json` и поместите его в корень проекта.

## Шаг 8: Запуск проекта

1. **Запустите FastAPI-сервер** (для обработки OAuth callback):
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000
   ```

2. **Запустите Telegram-бот**:
   ```bash
   python voicetotext.py
   ```

3. **Держите ngrok активным**:
   Убедитесь, что туннель ngrok работает в отдельном терминале.

## Шаг 9: Тестирование бота

1. Отправьте голосовое сообщение вашему Telegram-боту, например: "Создай событие Встреча завтра в 15:00".
2. Если авторизация не пройдена, бот отправит ссылку для OAuth. Перейдите по ней, чтобы предоставить доступ к Google Calendar.
3. После авторизации отправьте ещё одно голосовое сообщение — событие должно создаться или удалиться в Google Calendar.
