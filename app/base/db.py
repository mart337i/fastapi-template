from typing import Generator, Any
from app.base.logger import logger as _logger
from sqlmodel import create_engine, SQLModel, Session
import os

DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, Any, None]:
    with Session(engine) as session:
        yield session