import os
import telebot
import openai
from flask import Flask, request
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

# Логируем успешную загрузку переменных
print("✅ TELEGRAM_TOKEN loaded:", bool(TELEGRAM_TOKEN))
print("✅ OPENAI_API_KEY loaded:", bool(OPENAI_API_KEY))
print("✅ ASSISTANT_ID loaded:", bool(ASSISTANT_ID))

# Инициализация бота и OpenAI
bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY
app = Flask(__name__)

# Обработка входящих сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.send_chat_action(message.chat.id, "typing")

    # Создание Thread и отправка запроса к OpenAI Assistant
    thread = openai.beta.threads.create()
    openai.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=message.text,
    )
    run = openai.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID,
    )

    # Ожидание завершения выполнения
    while True:
        run_status = openai.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        if run_status.status == "completed":
            break

    # Получение и отправка ответа
    messages = openai.beta.threads.messages.list(thread_id=thread.id)
    for msg in reversed(messages.data):
        if msg.role == "assistant":
            response = msg.content[0].text.value
            bot.reply_to(message, response)
            break

# Обработка Webhook
@app.route("/", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

# Запуск Flask-приложения для Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render требует PORT
    app.run(host="0.0.0.0", port=port)
