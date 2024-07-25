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
    parsed_url = urlparse(url)
    if parsed_url.query == '':
        return url
    
    cleaned = ""
    for query in parsed_url.query.split('&'):
        key, val = query.split('=')
        if key in trackers:
            continue
    
        cleaned += key + '=' + val + '&'
    
    cleaned = cleaned[:-1]
    parsed_url = parsed_url._replace(query=cleaned)
    return parsed_url.geturl()

@bot.message_handler(func=lambda msg: True)
def handle_message(message):
    reply = "Cleaned urls:\n"
    detected = False
    if not message.entities:
        return
    
    for entity in message.entities:
        if entity.type != 'url':
            continue
        
        url = message.text[entity.offset:entity.offset + entity.length]
        cleaned = clean_url(url)
        if cleaned != url:
            detected = True 
            reply += cleaned + '\n'
    
    if detected:
        bot.reply_to(message, reply)

if __name__ == '__main__':
    print("Bot started")
    bot.infinity_polling()

