from telegram import Update, Bot
from telegram.ext import ContextTypes

from loguru import logger

from vlc import MediaPlayer

from radio.application import RadioApplication
from radio.db_model import AudioFile

STOP_PLAY = 'stop_play'

async def stop_play_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик нажатия на кнопку окончания воспроизведения музыки
    """
    app: RadioApplication = context.application
    bot: Bot =  context.bot

    await update.callback_query.answer()

    logger.info(f"Running audio file by request of {update.effective_user.name or update.effective_user.id}")

    if app.media_player:
        app.media_player.stop()
        app.media_player = None

    await bot.edit_message_reply_markup(
        chat_id = app.config.interact_id,
        message_id = update.callback_query.message.message_id,
        reply_markup = app.audio_relpy_markup
    )