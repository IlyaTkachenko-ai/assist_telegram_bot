import os
import telebot
import openai
from flask import Flask, request
from dotenv import load_dotenv
import time

load_dotenv(".env")

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY

@app.route("/", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    thread = openai.beta.threads.create()
    openai.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=message.text
    )
    run = openai.beta.threads.runs.create(thread_id=thread.id, assistant_id=ASSISTANT_ID)

    # ожидание завершения выполнения (упрощённо)
    while True:
        run_status = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if run_status.status == "completed":
            break
        time.sleep(1)

    messages = openai.beta.threads.messages.list(thread_id=thread.id)
    answer = messages.data[0].content[0].text.value
    bot.send_message(message.chat.id, answer)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
