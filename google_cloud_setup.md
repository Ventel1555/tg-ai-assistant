# Настройка Google Cloud Console для OAuth 2.0

Для интеграции с Google Calendar API необходимо создать проект в Google Cloud Console и получить файл `credentials.json`. Следуйте этим шагам:

## Создание проекта

1. Откройте [Google Cloud Console](https://console.cloud.google.com/).
2. Нажмите **Create Project** или выберите существующий проект.
3. Дайте проекту имя, например, `TelegramBotCalendar`.

## Включение Google Calendar API

1. В боковом меню выберите **APIs & Services** > **Library**.
2. Найдите **Google Calendar API** и нажмите **Enable**.

## Настройка OAuth Consent Screen

1. В меню **APIs & Services** выберите **OAuth consent screen**.
2. Выберите тип приложения:
   - **External** — для всех пользователей.
   - **Internal** — только для вашей организации.
3. Заполните обязательные поля:
   - **App name**: Например, `My Telegram Bot`.
   - **User support email**: Ваш email.
   - **Developer contact information**: Ваш email.
4. В разделе **Scopes** добавьте:
   - `https://www.googleapis.com/auth/calendar` (для управления календарём).
5. Сохраните изменения.

## Создание OAuth 2.0 Client ID

1. В меню **APIs & Services** выберите **Credentials**.
2. Нажмите **Create Credentials** > **OAuth 2.0 Client IDs**.
3. Выберите тип приложения **Web application**.
4. Укажите:
   - **Name**: Например, `Telegram Bot Client`.
   - **Authorized redirect URIs**: Введите `https://your-ngrok-domain.ngrok-free.app/oauth_callback` (замените `your-ngrok-domain` на ваш ngrok URL, который вы получите позже).
5. Нажмите **Create**, затем скачайте файл `credentials.json` и сохраните его в корне вашего проекта.