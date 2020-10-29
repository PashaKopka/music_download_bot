from __future__ import unicode_literals

from xxlimited import error

from aiogram import Bot, Dispatcher, executor, types

import os
import youtube_dl
import logging

API_TOKEN = 'set your api'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply('Hi!\nI\'m EchoBot!\nPowered by aiogram.')


@dp.message_handler(commands=['music'])
async def echo(message: types.Message):
    print(message.text[7:30])
    if message.text == '/music':
        await message.answer('You must send url:\n/music https://www.youtube.com/example')
    if message.text[7:31] == 'https://www.youtube.com/':
        ydl_opts = {
            # 'outtmpl': 'test',
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(message.text[7:], download=False)
            video_title = info_dict.get('title', None)
            video_id = info_dict.get("id", None)
            ydl.download([message.text[7:]])

        with open(f'{video_title}-{video_id}.mp3', 'rb') as f:
            data = f.read()

        await message.answer_audio(data)
        os.remove(f'{video_title}-{video_id}.mp3')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
