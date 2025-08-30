# Настройте Google Cloud Console для OAuth 2.0
## Вам нужно создать проект в Google Cloud Console и получить credentials.json.

Перейдите в Google Cloud Console

Откройте Google Cloud Console.
Нажмите Create Project или выберите существующий проект.
Дайте проекту имя, например, TelegramBotCalendar.


## Включите Google Calendar API

В боковом меню выберите APIs & Services > Library.
Найдите Google Calendar API и нажмите Enable.


## Настройте OAuth Consent Screen

В меню APIs & Services выберите OAuth consent screen.
Выберите External (если приложение для всех пользователей) или Internal (если только для вашей организации).
Заполните поля:

App name: Например, My Telegram Bot.
User support email: Ваш email.
Developer contact information: Ваш email.


## В разделе Scopes добавьте:

https://www.googleapis.com/auth/calendar (для управления календарём).


## Сохраните изменения.


Создайте OAuth 2.0 Client ID

В меню APIs & Services выберите Credentials.
Нажмите Create Credentials > OAuth 2.0 Client IDs.
Выберите тип приложения Web application.
Укажите:

Name: Например, Telegram Bot Client.
Authorized redirect URIs: Введите https://your-ngrok-domain.ngrok.io/oauth_callback (замените your-ngrok-domain на ваш ngrok URL, который вы получите позже).


Нажмите Create, затем скачайте файл credentials.json и сохраните его в корне вашего проекта.