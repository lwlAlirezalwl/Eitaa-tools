import telebot
import requests
import os
import sqlite3

# توکن ربات تلگرام
TOKEN = '6803428487:AAEy84BeXdepWLfTryQ84ofuaAYifZFchbQ'
# توکن API برای ارسال پیام
API_TOKEN = None
# Chat ID گروه یا کاربر
CHAT_ID = None

bot = telebot.TeleBot(TOKEN)

def set_data_by_telegram_channel(channel):

    conn = sqlite3.connect('sql.db')
    cursor = conn.cursor()
    cursor.execute('''
                SELECT * FROM messaging_data WHERE channel = ?
                    ''', (channel,))
    rows = cursor.fetchall()

    conn.close()
    
    if rows:
        
        API_TOKEN = rows[0].token
        CHAT_ID = rows[0].chat_id
        return True
    else:
        return False

def send_file(file_path,CAPTION):
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

def send_message(text):
    url = f'https://eitaayar.ir/api/{API_TOKEN}/sendMessage'
    data = {
        'chat_id': CHAT_ID,
        'text': text,
    }
    response = requests.post(url, data=data)
    print(response.text)

@bot.channel_post_handler(content_types=['document', 'video', 'audio', 'photo', 'voice', 'sticker', 'text'])
def handle_channel_post(message):
    if set_data_by_telegram_channel(message.chat.username):
        if message.content_type == 'text':
        # ارسال پیام با استفاده از API
      
            send_message(message.text)
        elif message.content_type in ['document', 'video', 'audio', 'photo', 'voice', 'sticker']:
        # در صورتی که پیام دارای پیوست باشد، فایل را ارسال می‌کنیم
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
            # دریافت آخرین عکس ارسال شده
                file_id = message.photo[-1].file_id
                file_name = 'photo.jpg'
            elif message.content_type == 'voice':
                file_id = message.voice.file_id
                file_name = 'voice.ogg'
            elif message.content_type == 'sticker':
                file_id = message.sticker.file_id
                file_name = 'sticker.webp'
        
        # اگر پیوست داشته باشد، فایل را ارسال کن
            if file_id:
            
            # دریافت اطلاعات فایل از تلگرام
                file_info = bot.get_file(file_id)
                file_path = file_info.file_path

            # دانلود فایل از تلگرام
                downloaded_file = bot.download_file(file_path)

            # ذخیره فایل در سیستم
                file_save_path = f'{file_name}'
                with open(file_save_path, 'wb') as new_file:
                    new_file.write(downloaded_file)

            # ارسال فایل به API
                send_file(file_save_path,CAPTION)

            # حذف فایل ذخیره شده پس از ارسال
                os.remove(file_save_path)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "ربات فعال شد.")

bot.infinity_polling()
