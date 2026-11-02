import os
import telebot
from dotenv import load_dotenv
import requests

load_dotenv()
bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

answers = {}


@bot.message_handler(commands=["start"])
def start(message):
    answers[message.chat.id] = {}
    bot.send_message(
        message.chat.id,
        "Здравствуйте! Задам 5 коротких вопросов, чтобы менеджер сразу понял вашу задачу.\n\n"
        "1/5. Как вас зовут?",
    )
    bot.register_next_step_handler(message, get_name)


def is_restart(message):
    if message.text == "/start":
        start(message)
        return True
    return False


def is_not_text(message, step):
    if message.text is None:
        bot.send_message(message.chat.id, "Пока я понимаю только текст. Напишите ответ, пожалуйста.")
        bot.register_next_step_handler(message, step)
        return True
    return False


def get_name(message):
    if is_restart(message):
        return
    if is_not_text(message, get_name):
        return
    answers[message.chat.id]["name"] = message.text
    bot.send_message(message.chat.id, "2/5. Чем занимается ваш бизнес?")
    bot.register_next_step_handler(message, get_niche)


def get_niche(message):
    if is_restart(message):
        return
    if is_not_text(message, get_niche):
        return
    answers[message.chat.id]["niche"] = message.text
    bot.send_message(message.chat.id, "3/5. Что нужно сделать?")
    bot.register_next_step_handler(message, get_need)


def get_need(message):
    if is_restart(message):
        return
    if is_not_text(message, get_need):
        return
    answers[message.chat.id]["need"] = message.text
    bot.send_message(
        message.chat.id,
        "4/5. Какой бюджет? Можно в сумах или долларах. Если пока не знаете, так и напишите.",
    )
    bot.register_next_step_handler(message, get_budget)


def get_budget(message):
    if is_restart(message):
        return
    if is_not_text(message, get_budget):
        return
    answers[message.chat.id]["budget"] = message.text
    bot.send_message(message.chat.id, "5/5. Когда нужно запустить?")
    bot.register_next_step_handler(message, get_deadline)


def get_deadline(message):
    if is_restart(message):
        return
    if is_not_text(message, get_deadline):
        return
    answers[message.chat.id]["deadline"] = message.text
    a = answers[message.chat.id]
    summary = (
        f"Имя: {a['name']}\n"
        f"Ниша: {a['niche']}\n"
        f"Задача: {a['need']}\n"
        f"Бюджет: {a['budget']}\n"
        f"Сроки: {a['deadline']}"
    )
    try:
        response = requests.post(WEBHOOK_URL, json={"text": summary}, timeout=10)
        response.raise_for_status()
        bot.send_message(
            message.chat.id,
            "Спасибо! Заявка передана менеджеру, он скоро свяжется с вами.\n\n" + summary,
        )
    except requests.RequestException:
        bot.send_message(
            message.chat.id,
            "Не получилось отправить заявку. Попробуйте ещё раз через несколько минут: /start",
        )


bot.infinity_polling()