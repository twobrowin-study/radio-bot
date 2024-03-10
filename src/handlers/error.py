from telegram import Update, Bot
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

import json, html
import traceback
from loguru import logger

from radio.application import RadioApplication

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Универсальный обработчик ошибок

    Логгирует ошибку в поток ошибок
    
    Также подгатавливает описание ошибки для высылки в рабочий чат:

    * При каком обновлении была ошибка

    * Что содержалась в данных чата

    * Что содержалось в пользовательских данных

    * Полный лог ошибки
    """

    app: RadioApplication = context.application

    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    logger.warning(f"Exception while handling an update: {tb_string}")

    update_str = update.to_dict() if isinstance(update, Update) else update if isinstance(update, dict) else str(update)
    messages_parts = [
        f"An exception was raised while handling an update",
        f"update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}",
        f"context.chat_data = {html.escape(str(context.chat_data))}",
        f"context.user_data = {html.escape(str(context.user_data))}",
        f"{html.escape(tb_string)}",
    ]
    messages = []
    for idx,message_part in enumerate(messages_parts):
        curr_len = len(message_part)
        template = "<pre>{message_part}</pre>\n\n" if idx > 0 else "{message_part}\n"
        if len(messages) > 0 and (len(messages[-1]) + curr_len <= 4096):
            messages[-1] += template.format(message_part=message_part)
        elif curr_len <= 4096:
            messages.append(template.format(message_part=message_part))
        else:
            for idx in range(0,curr_len,4096):
                messages.append(template.format(message_part=message_part[idx:idx+4096]))
    
    for message in messages:
        bot: Bot = app.bot
        await bot.send_message(app.config.interact_id, message, parse_mode = ParseMode.HTML)