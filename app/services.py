from datetime import datetime, timedelta

import time
import jwt
from cachetools import TTLCache

from database import cur,conn
from data import *
from models import UserInDB


def get_cache_access_time():
    """
    Метод для измерения времени доступа к кэшу
    """
    start_time = time.time()
    check_cache_status()
    end_time = time.time()
    return end_time - start_time


def get_database_access_time():
    """
    Метод для измерения времени доступа к базе данных
    """
    start_time = time.time()
    check_database_status()
    end_time = time.time()
    return end_time - start_time


def check_cache_status():
    """
    Метод для проверки статуса кэша
    """
    try:
        cache = TTLCache(maxsize=10, ttl=60)
        cache["test"] = "test"
        return True
    except Exception:
        return False


def check_database_status():
    """
    Метод для проверки статуса базы данных
    """
    try:
        cur.execute("SELECT 1")
        return True
    except Exception:
        return False


def get_user(username: str):
    """
    Метод для получения информации о пользователе из базы данных по его имени
    """
    cur.execute(
        "SELECT id, username, hashed_password FROM users WHERE username = %s",
        (username,),
    )
    user_data = cur.fetchone()
    if user_data:
        return UserInDB(
            id=user_data[0], username=user_data[1], hashed_password=user_data[2]
        )
    return None


def create_access_token(data: dict, expires_delta: timedelta):
    """
    Метод для создания JWT токена
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
