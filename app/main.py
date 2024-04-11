import os
from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.security import  OAuth2PasswordRequestForm
from passlib.context import CryptContext

from cachetools import TTLCache

from database import cur, conn
from models import UserInDB, UserInLogin, FilesResponse, File
from services import (
    check_cache_status,
    check_database_status,
    get_user,
    create_access_token,
    get_database_access_time,
    get_cache_access_time,
)
from data import *


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
app = FastAPI()
token_cache = TTLCache(maxsize=1000, ttl=ACCESS_TOKEN_EXPIRE_MINUTES * 60)


@app.get("/ping")
def check_services_status(
    cache_access_time: float = Depends(get_cache_access_time),
    db_access_time: float = Depends(get_database_access_time),
):
    """
    Проверяет статус кэша и бд
    """
    cache_status = check_cache_status()
    db_status = check_database_status()
    status = {
        "cache": cache_status,
        "cache_access_time": cache_access_time,
        "database": db_status,
        "database_access_time": db_access_time,
    }
    return status


@app.post("/files/upload")
async def upload_file_to_storage(file_path: str, username: str):
    """
    Загружает файл в бакет
    """
    if not os.path.exists(file_path):
        return {"message": "The file was not found"}

    token = token_cache.get(username)
    if token is None:
        return {"message": "Unauthorized"}

    file_name = os.path.basename(file_path)
    with open(file_path, "rb") as file:
        s3.upload_fileobj(file, BUCKET_NAME, file_name)

    cur.execute(
        "INSERT INTO files (name, created_at, path, size, username) VALUES (%s, %s, %s, %s, %s)",
        (file_name, datetime.utcnow(), file_path, os.path.getsize(file_path), username),
    )
    conn.commit()

    return {"message": "The file has been uploaded successfully"}


@app.get("/files/download")
async def download_file_from_storage(file_path: str, username: str):
    """
    Скачивает файл из бакета
    """
    token = token_cache.get(username)
    if token is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        file_object = s3.get_object(Bucket=BUCKET_NAME, Key=file_path)

        temp_file_path = f"/tmp/{os.path.basename(file_path)}"
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(file_object["Body"].read())

        return FileResponse(temp_file_path, filename=os.path.basename(file_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/register")
async def register_user(user: UserInLogin):
    """
    Регистрация

    """
    hashed_password = pwd_context.hash(user.password)
    cur.execute(
        "INSERT INTO users (username, hashed_password) VALUES (%s, %s)",
        (user.username, hashed_password),
    )
    conn.commit()
    return {"message": "User registered successfully"}


@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Авторизация.

    """
    user = get_user(form_data.username)
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    token_cache[user.username] = access_token

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/files/", response_model=FilesResponse)
async def get_user_files(username: str, user: UserInDB = Depends(get_user)):
    """
    Получает информацию о файлах пользователя

    """
    try:
        token = token_cache.get(username)
        if token is None:
            raise HTTPException(status_code=401, detail="Unauthorized")

        cur.execute(
            "SELECT id, name, created_at, path, size FROM files WHERE username = %s",
            (user.username,),
        )
        files_data = cur.fetchall()

        files = [
            File(
                id=file[0],
                username=user.username,
                name=file[1],
                created_at=str(file[2]),
                path=file[3],
                size=file[4],
                is_downloadable=True,
            )
            for file in files_data
        ]

        return FilesResponse(account_id=user.username, files=files)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cache")
async def view_cache():
    """
    Возвращает содержимое кэша
    """
    return token_cache.items()

