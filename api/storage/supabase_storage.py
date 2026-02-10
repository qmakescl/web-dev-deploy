from supabase import create_client, Client
from fastapi import UploadFile
from .base import StorageBackend
from ..config import settings
import uuid

class SupabaseStorage(StorageBackend):
    def __init__(self):
        self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        self.bucket_name = settings.STORAGE_BUCKET_NAME

    async def upload(self, file: UploadFile, filename: str) -> str:
        # 파일 확장자 유지하며 고유한 파일명 생성
        ext = filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{ext}"
        
        content = await file.read()
        
        try:
            # Supabase 스토리지에 업로드
            self.client.storage.from_(self.bucket_name).upload(
                path=unique_filename,
                file=content,
                file_options={"content-type": file.content_type}
            )
            return self.get_public_url(unique_filename)
        except Exception as e:
            print(f"Supabase upload error: {e}")
            raise e

    async def delete(self, file_url: str) -> bool:
        # URL에서 파일명 추출 (Supabase 특정 URL 구조 가정)
        # 예: https://.../storage/v1/object/public/bucket/filename.png
        filename = file_url.split("/")[-1]
        try:
            self.client.storage.from_(self.bucket_name).remove([filename])
            return True
        except Exception as e:
            print(f"Supabase delete error: {e}")
            return False

    def get_public_url(self, filename: str) -> str:
        return self.client.storage.from_(self.bucket_name).get_public_url(filename)
