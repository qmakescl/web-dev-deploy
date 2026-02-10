import os
import shutil
from fastapi import UploadFile
from .base import StorageBackend
import uuid

class LocalStorage(StorageBackend):
    def __init__(self):
        self.upload_dir = "uploads"
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)

    async def upload(self, file: UploadFile, filename: str) -> str:
        ext = filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{ext}"
        file_path = os.path.join(self.upload_dir, unique_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return self.get_public_url(unique_filename)

    async def delete(self, file_url: str) -> bool:
        filename = file_url.split("/")[-1]
        file_path = os.path.join(self.upload_dir, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

    def get_public_url(self, filename: str) -> str:
        # 로컬 개발 환경에서는 /api/uploads/{filename} 또는 /uploads/{filename}으로 서빙 가정
        return f"/uploads/{filename}"
