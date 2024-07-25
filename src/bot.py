import os
import telebot
from dotenv import load_dotenv
import re
from urllib.parse import urlparse

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
trackers = set(os.getenv('TRACKERS').split(','))

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hi, time to get rid of some tracking params")


def clean_url(url): 
    d = urlparse(url)
    if d.query == '':
        return url
    qu = ""
    for q in d.query.split('&'):
        key, val = q.split('=')
        if key in trackers:
            continue
        qu += key + '=' + val + '&'
    qu = qu[:-1]
    d = d._replace(query=qu)
    return d.geturl()


@bot.message_handler(func=lambda msg: True)
def handle_message(message):
    reply = "Cleaned urls:\n"
    detected = False
    if not message.entities:
        return
    for e in message.entities:
        if e.type != 'url':
            continue
        u = message.text[e.offset:e.offset + e.length]
        cleaned = clean_url(u)
        if cleaned != u:
            detected = True 
            reply += clean_url(u) + '\n'
    if detected:
        bot.reply_to(message, reply)

if __name__ == '__main__':
    print("Bot started")
    bot.infinity_polling()

