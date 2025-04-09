import os
import json
from flask import Flask, request
from dotenv import load_dotenv
import telebot

# Загрузка переменных окружения из .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Проверка загрузки токена
if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN не найден в переменных окружения")

print("✅ TELEGRAM_TOKEN загружен")

# Инициализация бота и Flask
bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

@app.route("/", methods=["POST"])
def webhook():
    try:
        json_string = request.get_data().decode("utf-8")
        print("[DEBUG] Raw JSON from Telegram:")
        print(json_string)

        update = telebot.types.Update.de_json(json.loads(json_string))
        print("[DEBUG] Update parsed, calling process_new_updates")

        bot.process_new_updates([update])
    except Exception as e:
        print(f"[ERROR in webhook] {e}")
    return "OK", 200

# Простой хендлер — отвечает на любое сообщение
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    print(f"[HANDLER] Message received from {message.chat.id}: {message.text}")
    bot.send_message(message.chat.id, f"Ты написал: {message.text}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # по умолчанию порт 5000
    print(f"✅ Starting app on port {port}")
    app.run(host="0.0.0.0", port=port)
