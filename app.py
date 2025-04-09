import os
from flask import Flask, request
from dotenv import load_dotenv
import telebot
import openai

# Загрузка переменных окружения из .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

# Логируем значения
print(f"✅ TELEGRAM_TOKEN loaded: {bool(TELEGRAM_TOKEN)}")
print(f"✅ OPENAI_API_KEY loaded: {bool(OPENAI_API_KEY)}")
print(f"✅ ASSISTANT_ID loaded: {bool(ASSISTANT_ID)}")

openai.api_key = OPENAI_API_KEY

app = Flask(__name__)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@app.route("/", methods=["GET"])
def index():
    return "✅ Bot is alive", 200

@app.route("/", methods=["POST"])
def webhook():
    print("🔔 Webhook вызван!")
    if request.headers.get("Content-Type") != "application/json":
        print("❌ Content-Type неправильный:", request.headers.get("Content-Type"))
        return "Invalid Content-Type", 400

    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK", 200

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    print(f"📩 Получено сообщение от @{message.from_user.username}: {message.text}")

    try:
        thread = openai.beta.threads.create()
        print(f"🧵 Создан новый thread: {thread.id}")

        openai.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=message.text
        )

        run = openai.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )

        print(f"⚙️ Запущен run: {run.id}, ожидаем завершения...")

        while True:
            run_status = openai.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if run_status.status == "completed":
                break

        messages = openai.beta.threads.messages.list(thread_id=thread.id)
        response = messages.data[0].content[0].text.value
        print("✅ Ответ получен:", response)

        bot.send_message(message.chat.id, response)

    except Exception as e:
        print(f"❌ Ошибка при обработке запроса: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при обработке запроса.")
