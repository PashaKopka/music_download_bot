from __future__ import unicode_literals
from aiogram import Bot, Dispatcher, executor, types
from apiclient.discovery import build
from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

import os
import youtube_dl
import logging

from . import settings

logging.basicConfig(level=logging.INFO)
bot = Bot(token=settings.API_TOKEN)
dp = Dispatcher(bot)
download_callback = CallbackData('https', 'url')


def download_music_file(url: str) -> (bytes, str):
    """
    This function download video from youtube and save it to mp3-file

    :param url: link on youtube video (must starts with 'https://www.youtube.com/watch?v=')
    :return: tuple of data from mp3 file and name of mp3 file
    """
    # TODO downloading in some directory
    with youtube_dl.YoutubeDL(settings.MP3_FILE_OPTIONS) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        filename = f'{info_dict.get("title", None)}-{info_dict.get("id", None)}.mp3'
        ydl.download([url])

    with open(filename, 'rb') as f:
        data = f.read()

    return data, filename


def get_video_id(request: str) -> list:
    """
    This function use youtube api v3 to search videos

    :param request:
    :return: the first 5 videos that are the result of the search
    """
    youtube_searcher = build('youtube', 'v3', developerKey=settings.YOUTUBE_API)
    req = youtube_searcher.search().list(q=request, part='snippet', type='video')
    result = req.execute()

    id_array = []
    for item in result['items']:
        id_array.append(item['id']['videoId'])

    return id_array


async def send_music_file(message_data):
    """
    This function send mp3-file to user

    :param message_data: this parameter must be Message or CallbackQuery
    :return:
    """
    if isinstance(message_data, types.Message):
        data, filename = download_music_file(message_data)
        await message_data.answer_audio(data)
    else:
        data, filename = download_music_file(message_data.data)
        await message_data.message.answer_audio(data)

    os.remove(filename)


async def send_download_button(url):
    """
    This function make download button

    :param url: link on youtube video
    :return: Keyboard
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='download', callback_data=download_callback.new(
                url=url[6:]
            ))
        ]
    ])


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply(
        """
        Hi, it is bot for downloading music from youtube.
        This is how to use it:
        /music [link to video]
            bot will send you mp3-file.
        /search [request]
            bot will send you first 5 videos that are the result of 
            searching on YouTube and then you can choose your video.
        """
    )


@dp.callback_query_handler(text_contains='https')
async def download_music_using_button(call: CallbackQuery):
    """
    This function handle button pressing
    :param call: Callback from button
    :return:
    """
    await send_music_file(call)


@dp.message_handler(commands=['music'])
async def download_music(message: types.Message):
    """
    This function handle url sent by user

    :param message:
    :return:
    """
    if message.text == '/music':
        await message.answer('You must send url:\n/music https://www.youtube.com/example')
    if message.text[7:31] == 'https://www.youtube.com/':
        await send_music_file(message)


@dp.message_handler(commands=['search'])
async def search(message: types.Message):
    """
    This function handle searching of video on YouTube

    :param message:
    :return:
    """
    if message.text != '/search':
        id_array = get_video_id(message.text[8:])
        for video_id in id_array:
            url = settings.YOUTUBE_URL + video_id
            choice = send_download_button(url)
            await message.answer(text=url, reply_markup=choice)
    else:
        await message.answer('You must send request:\n/search your text')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
