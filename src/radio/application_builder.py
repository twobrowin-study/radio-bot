from telegram.ext import ApplicationBuilder

from loguru import logger

from radio.application import RadioApplication
from radio.config_model import create_config

class RadioApplicationBuilder(ApplicationBuilder):
    """
    Переопределённый класс `ApplicationBuilder` для нужд этого приложения

    При инициализации создаёт конфигурацию прилоежния из yaml файла

    После создания конфигурации использует токен из неё и класс `RadioApplication` для инициализации
    """

    def __init__(self):
        super().__init__()

        try:
            self._config = create_config()
            logger.info(self._config.model_dump_json(indent=4))
        except Exception as exc:
            logger.opt(exception=True).error(f"Error initializing configuration: {str(exc)}")
            exit(1)

        self._token = self._config.token
        self._application_class = RadioApplication
        self._application_kwargs = {'config': self._config}