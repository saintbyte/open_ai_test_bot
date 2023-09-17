import logging
import os
from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from peewee import *
from playhouse.db_url import connect

load_dotenv()
logger = logging.getLogger(__name__)


def get_bot() -> Bot:
    token: Optional[str] = os.environ.get("BOT_TOKEN")
    if token is None:
        logger.error("BOT_TOKEN not defined in .env . Halt.")
        quit()
    return Bot(token, parse_mode=ParseMode.HTML)


def get_openai_endpoint() -> str:
    endpoint = os.environ.get("OPENAI_ENDPOINT")
    if endpoint is None:
        logger.error("OPENAI_ENDPOINT not defined in .env . Halt.")
        quit()
    return endpoint


def get_database_connection() -> Database:
    database_url = os.environ.get("DATABASE_URL")
    if database_url is None:
        logger.error("DATABASE_URL not defined in .env . Halt.")
        quit()
    pg_db = connect(database_url)
    return pg_db
