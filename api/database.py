"""Подключаем sqlalchemy"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from dotenv import load_dotenv

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER_local")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD_local")
POSTGRES_DB = os.getenv("POSTGRES_DB_local")
DB_HOST = os.getenv("DB_HOST_local")
DB_PORT = os.getenv("DB_PORT_local")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{DB_PORT}/{POSTGRES_DB}?client_encoding=UTF8"



engine = create_engine(DATABASE_URL, echo=True)

