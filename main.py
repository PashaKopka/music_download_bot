from __future__ import unicode_literals

from aiogram import Bot, Dispatcher, executor, types

import os
import youtube_dl
import logging

API_TOKEN = '1329098332:AAF1yP2menisi0uE3P5CSP5MnvcuNoiW-iY'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply('Hi!\nI\'m EchoBot!\nPowered by aiogram.')


def set_options():
    return {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }


def download_music(url):
    options = set_options()

    with youtube_dl.YoutubeDL(options) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        filename = f'{info_dict.get("title", None)}-{info_dict.get("id", None)}.mp3'
        ydl.download([url])

    with open(filename, 'rb') as f:
        data = f.read()

    return data, filename


@dp.message_handler(commands=['music'])
async def echo(message: types.Message):
    if message.text == '/music':
        await message.answer('You must send url:\n/music https://www.youtube.com/example')
    if message.text[7:31] == 'https://www.youtube.com/':
        data, filename = download_music(message.text[7:])

        await message.answer_audio(data)
        os.remove(filename)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
