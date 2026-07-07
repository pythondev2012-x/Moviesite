from pyrogram import Client
from django.conf import settings

app = Client(
    "kino_stream",
    api_id=settings.TELEGRAM_API_ID,
    api_hash=settings.TELEGRAM_API_HASH,
    bot_token=settings.TELEGRAM_BOT_TOKEN,
    in_memory=True
)