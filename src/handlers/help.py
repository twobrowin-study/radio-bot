from telegram import Update
from telegram.ext import ContextTypes

from loguru import logger

from radio.application import RadioApplication

HELP_COMMAND = 'help'

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды help
    """

    app: RadioApplication = context.application

    logger.info(f"Got help request from {update.effective_user.id}")

    await update.message.reply_markdown(app.config.help_markdown)