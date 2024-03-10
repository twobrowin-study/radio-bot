from telegram import Update, Bot
from telegram.ext import ContextTypes

from loguru import logger

from vlc import MediaPlayer

from radio.application import RadioApplication
from radio.db_model import AudioFile

from handlers.audio_done import audio_stop_callback

RUN_IMMEDIATELY = 'run_immediately'

async def run_immediately_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик нажатия на кнопку непосредственного запуска музыки
    """
    app: RadioApplication = context.application
    bot: Bot =  context.bot

    await update.callback_query.answer()

    with app.db_sessionmaker() as session:
        audio_file = session.query(AudioFile).filter_by(message_id = update.callback_query.message.message_id).one()
    
    logger.info(f"Running audio file {audio_file.file_name} by request of {update.effective_user.name or update.effective_user.id}")
    
    if app.media_player:
        app.media_player.stop()

    media_player: MediaPlayer = MediaPlayer(app.file_dir / audio_file.file_name)
    media_player.play()

    app.media_player = media_player

    await bot.edit_message_reply_markup(
        chat_id = app.config.interact_id,
        message_id = update.callback_query.message.message_id,
        reply_markup = app.stop_relpy_markup
    )

    app.job_queue.run_once(audio_stop_callback, when = audio_file.duration, data = audio_file)