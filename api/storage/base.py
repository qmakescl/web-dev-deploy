from abc import ABC, abstractmethod
from fastapi import UploadFile

class StorageBackend(ABC):
    @abstractmethod
    async def upload(self, file: UploadFile, filename: str) -> str:
        """Uploads a file and returns the public URL."""
        pass

    @abstractmethod
    async def delete(self, file_url: str) -> bool:
        """Deletes a file given its URL."""
        pass

    @abstractmethod
    def get_public_url(self, filename: str) -> str:
        """Returns the public URL for a given filename."""
        pass
