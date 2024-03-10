from telegram import Update
from telegram.ext import ContextTypes

from loguru import logger

import vlc

from radio.application import RadioApplication
from radio.db_model import AudioFiles

RUN_IMMEDIATELY = 'run_immediately'

async def run_immediately_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик нажатия на кнопку непосредственного запуска музыки
    """
    app: RadioApplication = context.application

    await update.callback_query.answer()

    with app.db_sessionmaker() as session:
        audio_file = session.query(AudioFiles).filter_by(message_id = update.callback_query.message.message_id).one()
    
    logger.info(f"Running audio file {audio_file.file_name} by request of {update.effective_user.name or update.effective_user.id}")
    
    media: vlc.MediaPlayer = vlc.MediaPlayer(app.file_dir / audio_file.file_name)
    media.play()