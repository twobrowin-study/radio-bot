from telegram.ext import (
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler
)
from telegram.ext.filters import (
    Chat,
    VOICE,
    AUDIO
)

from loguru import logger

from radio.application_builder import RadioApplicationBuilder
from radio.application import RadioApplication

from handlers.error import error_handler
from handlers.help import help_handler, HELP_COMMAND
from handlers.audio import audio_types_handler
from handlers.run_immediately import run_immediately_callback_handler, RUN_IMMEDIATELY

if __name__ == "__main__":
    logger.info("Starting an application...")
    app: RadioApplication = RadioApplicationBuilder().build()
    
    app.add_error_handler(error_handler)

    interact_chat_filter = Chat(app.config.interact_id)

    app.add_handler(CommandHandler(HELP_COMMAND, help_handler, filters=interact_chat_filter, block=False))

    app.add_handler(MessageHandler(
        (VOICE | AUDIO) & interact_chat_filter,
        audio_types_handler,
        block=False
    ))

    app.add_handlers([
        CallbackQueryHandler(run_immediately_callback_handler, pattern=RUN_IMMEDIATELY, block=False),
    ])

    app.run_polling()
    logger.info("Done! Have a greate day!")