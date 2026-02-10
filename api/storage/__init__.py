from ..config import settings
from .base import StorageBackend
from .supabase_storage import SupabaseStorage
from .local_storage import LocalStorage

def get_storage_backend() -> StorageBackend:
    if settings.STORAGE_BACKEND == "supabase":
        return SupabaseStorage()
    else:
        return LocalStorage()

storage_backend = get_storage_backend()
