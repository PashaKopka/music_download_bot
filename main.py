from __future__ import unicode_literals
from aiogram import Bot, Dispatcher, executor, types
from apiclient.discovery import build
from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

import os
import youtube_dl
import logging

API_TOKEN = '1329098332:AAF1yP2menisi0uE3P5CSP5MnvcuNoiW-iY'
YOUTUBE_API = 'AIzaSyBWhXU8Ug6B3e17GoSQ22RT4jVDRD3iYN4'
SEARCH_URL = 'https://www.youtube.com/results?search_query='

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


def set_options():
    return {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }


def _download_music(url):
    options = set_options()

    with youtube_dl.YoutubeDL(options) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        filename = f'{info_dict.get("title", None)}-{info_dict.get("id", None)}.mp3'
        ydl.download([url])

    with open(filename, 'rb') as f:
        data = f.read()

    return data, filename


def get_video_id(request):
    youtube_searcher = build('youtube', 'v3', developerKey=YOUTUBE_API)
    req = youtube_searcher.search().list(q=request, part='snippet', type='video')
    res = req.execute()

    id_arr = []
    for item in res['items']:
        id_arr.append(item['id']['videoId'])

    return id_arr


download_callback = CallbackData('https', 'url')

# choice = InlineKeyboardMarkup(inline_keyboard=[
#     [
#         InlineKeyboardButton(text='download', callback_data=download_callback.new(
#             url='pear'
#         ))
#     ]
# ])


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply('Hi!\nI\'m EchoBot!\nPowered by aiogram.')


@dp.callback_query_handler(text_contains='https')
async def download_music_using_button(call: CallbackQuery):
    data, filename = _download_music(call.data)

    await call.message.answer_audio(data)
    os.remove(filename)


@dp.message_handler(commands=['music'])
async def download_music(message: types.Message):
    if message.text == '/music':
        await message.answer('You must send url:\n/music https://www.youtube.com/example')
    if message.text[7:31] == 'https://www.youtube.com/':
        data, filename = _download_music(message.text[7:])

        await message.answer_audio(data)
        os.remove(filename)


@dp.message_handler(commands=['search'])
async def search(message: types.Message):
    if message.text != '/search':
        print(f'\n{message.text[8:]}\n')
        id_arr = get_video_id(message.text[8:])
        for id in id_arr:
            url = f'https://www.youtube.com/watch?v={id}'
            choice = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text='download', callback_data=download_callback.new(
                        url=url[6:]
                    ))
                ]
            ])
            await message.answer(text=url, reply_markup=choice)
    else:
        await message.answer('You must send request:\n/search your text')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
