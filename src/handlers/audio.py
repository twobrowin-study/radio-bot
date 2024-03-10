from telegram import Update
from telegram.ext import ContextTypes

from datetime import datetime
from loguru import logger

from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError

from radio.application import RadioApplication
from radio.db_model import AudioFiles

async def audio_types_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик файлов аудио типов: голосовых сообщений, аудиофайлов, zip архивов

    Обработчик возвращает этот же файл в чат с набором inline-кнопок, позволяющих управлять 
    
    Сам аудиофайл или архив сохраняется на диске и его описание добавляется в БД для быстрого запуска в будущем
    """
    app: RadioApplication = context.application

    file_name = None

    if update.message.voice:
        logger.info(f"Got voice from {update.effective_user.id}")

        user_name = update.effective_user.name or update.effective_user.id
        file_name = f"voice_{user_name}_{datetime.now().strftime('%Y_%m%d_%H%M%S%f')}.ogg"
        
        reply_message = await update.message.reply_voice(
            voice = update.message.voice,
            duration = update.message.voice.duration,
            reply_markup = app.audio_relpy_markup
        )

    if update.message.audio:
        logger.info(f"Got audio from {update.effective_user.id}")

        file_extention = update.message.audio.file_name.split('.')[-1]
        file_name = f"{update.message.audio.performer}_{update.message.audio.title}.{file_extention}"

        reply_message = await update.message.reply_audio(
            audio = update.message.audio,
            duration = update.message.audio.duration,
            performer = update.message.audio.performer,
            title = update.message.audio.title,
            reply_markup = app.audio_relpy_markup
        )
    
    logger.info(f"Saving audiofiles for later")
    file = await update.message.effective_attachment.get_file()
    file_name = file_name or file.file_id
    await file.download_to_drive(app.file_dir / file_name)

    logger.info(f"Saving information about file into DB")
    with app.db_sessionmaker() as session:
        session.execute(
            insert(AudioFiles).values(
                message_id = reply_message.id,
                file_name  = file_name
            )
        )
        try:
            session.commit()
        except IntegrityError as err:
            logger.error(err)
            session.rollback()
