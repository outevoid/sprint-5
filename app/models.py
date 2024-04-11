from typing import List
from pydantic import BaseModel

class User(BaseModel):
    user_id: int

class UserInDB(BaseModel):
    username: str
    hashed_password: str

class UserInLogin(BaseModel):
    username: str
    password: str

class FileUploadRequest(BaseModel):
    path: str

class File(BaseModel):
    id: int
    username: str
    name: str
    created_at: str
    path: str
    size: int
    is_downloadable: bool

class FilesResponse(BaseModel):
    account_id: str
    files: List[File]