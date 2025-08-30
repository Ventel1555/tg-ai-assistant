import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from aiogram import Bot
from stt import handle_oauth_callback 

app = FastAPI()

load_dotenv()
# Инициализация проекта
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

@app.get("/oauth_callback")
async def oauth_callback(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    if not code or not state:
        return HTMLResponse("Ошибка: отсутствует код или состояние.")
    await handle_oauth_callback(code, state, bot)
    return HTMLResponse("Авторизация завершена. Вернитесь в Telegram.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)