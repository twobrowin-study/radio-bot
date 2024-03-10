import os
import yaml
from dotenv import load_dotenv, find_dotenv
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)

class ConfigYaml(BaseSettings):
    """
    Основной класс конфигурации прилоежния

    Поддерживается установка полей конфигурации при помощи переменных окружения

    Например, `TOKEN`, `INTERACT_ID`

    В случае, если требуется переписать вложенные словари, следует их разделять символами `__`

    Например, `VOICE_REPLY__RUN_IMMEDIATELY`
    """

    model_config = SettingsConfigDict(env_nested_delimiter='__')

    token: str
    interact_id: int
    file_dir: str
    db_uri: str

    my_name: str
    my_commands: dict[str, str]

    help_markdown: str
    
    audio_reply: dict[str, str]
    stop_play:   str
    
def create_config() -> ConfigYaml:
    """
    Создание конфига из файла и переменных окружения
    """

    load_dotenv(find_dotenv())
    CONFIG = os.getenv('CONFIG')

    if not CONFIG:
        raise Exception("Please add CONFIG to system env or .env for development")

    with open(CONFIG, "r") as stream:
        full_config = yaml.safe_load(stream)

    return ConfigYaml(**full_config)