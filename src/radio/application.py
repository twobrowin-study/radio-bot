import os
from asyncio import Queue
from typing import Any, Callable, Coroutine
from telegram.ext import Application
from telegram.ext._basepersistence import BasePersistence
from telegram.ext._baseupdateprocessor import BaseUpdateProcessor
from telegram.ext._contexttypes import ContextTypes
from telegram.ext._updater import Updater

from telegram import (
    Bot, BotName, BotCommand,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pathlib import Path
from loguru import logger

from radio.config_model import ConfigYaml
from radio.db_model import Base

class RadioApplication(Application):
    """
    Переопределённый класс приложения со специфическими настройками, требуемыми для этого бота

    При инициализации подменяет функцию `post_init` если она не задана

    Содержит поле `config` с полной конфигурацей приложения
    """

    def __init__(self, *, config: ConfigYaml, bot: Any,
                 update_queue: Queue[object], updater: Updater | None,
                 job_queue: Any, update_processor: BaseUpdateProcessor,
                 persistence: BasePersistence | None, context_types: ContextTypes,
                 post_init: Callable[[Application], Coroutine[Any, Any, None]] | None,
                 post_shutdown: Callable[[Application], Coroutine[Any, Any, None]] | None,
                 post_stop: Callable[[Application], Coroutine[Any, Any, None]] | None):
        """
        Инциализация собственого приложения и начитка конфигруации

        Подменяет `post_init` функцию на внутреннюю если она не задана

        Получает конфигурацию в качестве параметра `config`
        """
        super().__init__(bot=bot, update_queue=update_queue, updater=updater,
                         job_queue=job_queue, update_processor=update_processor,
                         persistence=persistence, context_types=context_types,
                         post_init=post_init if post_init else self._post_init,
                         post_shutdown=post_shutdown,
                         post_stop=post_stop)
        
        self.config = config

        self.audio_relpy_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(text=text, callback_data=callback_data)]
            for callback_data,text in self.config.audio_reply.items()
        ])

        self.file_dir = Path(self.config.file_dir)

        self.db_engine = create_engine(
            self.config.db_uri, 
            echo=True,
            pool_size=10,
            max_overflow=2,
            pool_recycle=300,
            pool_pre_ping=True,
            pool_use_lifo=True
        )
        self.db_sessionmaker = sessionmaker(bind = self.db_engine)

    async def _post_init(self, application: Application) -> None:
        """
        Стандартная функция инициализации бота

        * Устанавливает имя бота

        * Устанавливает команды бота

        * Проверяет наличие директрии для сохранения файлов и создаёт если её нет

        * Проверяет наличие базы данных и создаёт если её нет
        """
        bot: Bot = self.bot

        bot_my_name: BotName = await bot.get_my_name()
        if bot_my_name.name != self.config.my_name:
            await bot.set_my_name(self.config.my_name)
            logger.info("Found difference in my name - updated")

        my_comands: tuple[BotCommand] = await bot.get_my_commands()
        my_comands_config = tuple(BotCommand(comand, description) for comand,description in self.config.my_commands.items())

        if my_comands != my_comands_config:
            await bot.set_my_commands(my_comands_config)
            logger.info("Found difference in my commands - updated")
        
        self.file_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Checked and created file save directory - {self.config.file_dir}")

        Base.metadata.create_all(self.db_engine)
        logger.info("Created database metadata")

        logger.info("Done post init procedure")