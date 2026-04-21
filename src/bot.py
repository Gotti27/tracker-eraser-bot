import os
import re
from io import BytesIO
from urllib.parse import urlparse

import instaloader
import requests
import telebot
from dotenv import load_dotenv
from telebot.types import Message, ReplyParameters

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
trackers = set(os.getenv('TRACKERS').split(','))

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hi, time to get rid of some tracking params")


def is_valid_instagram_reel_url(url):
    # Matches standard, mobile, and 'p' or 'reel' paths
    pattern = r"^(https?://)?(www\.)?instagram\.com/(reel)/[a-zA-Z0-9_-]+/"
    return bool(re.match(pattern, url))


def get_reel_blob(url):
    L = instaloader.Instaloader()

    shortcode = url.split("/")[-2]
    post = instaloader.Post.from_shortcode(L.context, shortcode)

    if not post.is_video:
        return None

    response = requests.get(post.video_url, stream=True)
    response.raise_for_status()

    video_blob = BytesIO(response.content)
    return video_blob


def clean_url(url):
    parsed_url = urlparse(url)
    if parsed_url.query == '':
        return url

    cleaned = ""
    for query in parsed_url.query.split('&'):
        q = query.split('=')
        key = q[0]
        val = q[1]
        if key in trackers:
            continue

        cleaned += key + '=' + val + '&'

    cleaned = cleaned[:-1]
    parsed_url = parsed_url._replace(query=cleaned)
    return parsed_url.geturl()


@bot.message_handler(func=lambda msg: True)
def handle_message(message: Message):
    reply = "Cleaned urls:\n"
    detected = False
    video = None
    if not message.entities:
        return

    for entity in message.entities:
        if entity.type != 'url':
            continue

        url = message.text[entity.offset:entity.offset + entity.length]
        cleaned = clean_url(url)

        if is_valid_instagram_reel_url(cleaned):
            blob = get_reel_blob(cleaned)
            video = telebot.types.InputFile(blob)

        if cleaned != url:
            detected = True
            reply += cleaned + '\n'

    if video is not None:
        bot.send_video(message.chat.id, video=video, reply_parameters=ReplyParameters(message.message_id),
                       caption=reply if detected else None)
    elif detected:
        bot.reply_to(message, reply)


if __name__ == '__main__':
    print("Bot started")
    bot.infinity_polling()
