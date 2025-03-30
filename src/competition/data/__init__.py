"""
Storage providers for competition data.
"""
from .storage import StorageProvider, LocalStorageProvider, FirebaseStorageProvider

__all__ = ['StorageProvider', 'LocalStorageProvider', 'FirebaseStorageProvider'] 