from telegram import Bot
from telegram.ext import CallbackContext

from loguru import logger

from radio.application import RadioApplication
from radio.db_model import AudioFile

async def audio_stop_callback(context: CallbackContext) -> None:
    app: RadioApplication = context.application
    bot: Bot = context.bot

    audio_file: AudioFile = context.job.data

    logger.info(f"Propably done playng audio file {audio_file.file_name} - reseting buttons")

    await bot.edit_message_reply_markup(
        chat_id = app.config.interact_id,
        message_id = audio_file.message_id,
        reply_markup = app.audio_relpy_markup
    )