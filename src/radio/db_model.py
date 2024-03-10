from sqlalchemy.orm import (
    Mapped, 
    mapped_column,
    MappedAsDataclass, 
    DeclarativeBase
)

class Base(MappedAsDataclass, DeclarativeBase):
    pass

class AudioFile(Base):
    """
    Таблица базы данных, в которую вносится информация:

    * Соответтсвие имени файла и сообщения, в котором оно было выслано

    * Имя файла на диске
    """

    __tablename__ = "audio_files"

    id:         Mapped[int] = mapped_column(primary_key=True, nullable=False)
    message_id: Mapped[int] = mapped_column(nullable=False, index=True, unique=True)
    file_name:  Mapped[str] = mapped_column(nullable=False, index=True, unique=True)
    duration:   Mapped[int] = mapped_column(nullable=False)
