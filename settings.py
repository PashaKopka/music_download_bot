TELEGRAM_API_TOKEN = '-'
YOUTUBE_API = '-'
SEARCH_URL = 'https://www.youtube.com/results?search_query='
YOUTUBE_URL = 'https://www.youtube.com/watch?v='

MP3_FILE_OPTIONS = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}
