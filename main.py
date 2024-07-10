import telebot
import requests
import os
import sqlite3

TOKEN = "telegram bot token"

bot = telebot.TeleBot(TOKEN)


def get_data_by_telegram_channel(channel):
    conn = sqlite3.connect('sql.db')
    cursor = conn.cursor()
    cursor.execute('''
                SELECT * FROM messaging_data WHERE channel = ?
                    ''', (channel,))
    rows = cursor.fetchall()

    conn.close()

    return rows


def send_file(file_path, CAPTION,API_TOKEN,CHAT_ID):
    url = f'https://eitaayar.ir/api/{API_TOKEN}/sendFile'
    files = {
        'file': open(file_path, 'rb')
    }
    data = {
        'chat_id': CHAT_ID,
        # 'title': TITLE,
        'caption': CAPTION,
        # 'date': int(time()) + 30
    }
    response = requests.post(url, files=files, data=data, verify=False)
    print(response.text)


def send_message(text,API_TOKEN,CHAT_ID):
    url = f'https://eitaayar.ir/api/{API_TOKEN}/sendMessage'
    data = {
        'chat_id': CHAT_ID,
        'text': text,
    }
    response = requests.post(url, data=data)
    print(response.text)


@bot.channel_post_handler(content_types=['document', 'video', 'audio', 'photo', 'voice', 'sticker', 'text'])
def handle_channel_post(message):
    data = get_data_by_telegram_channel(message.chat.username)
    if data:
        API_TOKEN = data[0][2]
        CHAT_ID = data[0][3]
        if message.content_type == 'text':

            send_message(message.text,API_TOKEN,CHAT_ID)
        elif message.content_type in ['document', 'video', 'audio', 'photo', 'voice', 'sticker']:

            file_id = None
            file_name = None
            CAPTION = message.text

            if message.content_type == 'document':
                file_id = message.document.file_id
                file_name = message.document.file_name
            elif message.content_type == 'video':
                file_id = message.video.file_id
                file_name = 'video.mp4'
            elif message.content_type == 'audio':
                file_id = message.audio.file_id
                file_name = 'audio.mp3'
            elif message.content_type == 'photo':
                file_id = message.photo[-1].file_id
                file_name = 'photo.jpg'
            elif message.content_type == 'voice':
                file_id = message.voice.file_id
                file_name = 'voice.ogg'
            elif message.content_type == 'sticker':
                file_id = message.sticker.file_id
                file_name = 'sticker.webp'

            if file_id:
                file_info = bot.get_file(file_id)
                file_path = file_info.file_path

                downloaded_file = bot.download_file(file_path)

                file_save_path = f'{file_name}'
                with open(file_save_path, 'wb') as new_file:
                    new_file.write(downloaded_file)

                send_file(file_save_path, CAPTION,API_TOKEN,CHAT_ID)

                os.remove(file_save_path)


bot.infinity_polling()
