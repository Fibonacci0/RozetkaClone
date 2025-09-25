import uuid
import os
from django.core.files.storage import Storage
from azure.storage.blob import BlobServiceClient
from django.conf import settings
from azure.core.exceptions import ResourceNotFoundError

class AzureBaseStorage(Storage):
    container_name = None

    def __init__(self):
        if not self.container_name:
            raise ValueError("Container name must be defined in subclass.")
        self.account_name = settings.AZURE_ACCOUNT_NAME
        self.account_key = settings.AZURE_ACCOUNT_KEY
        self.blob_service = BlobServiceClient(
            account_url=f"https://{self.account_name}.blob.core.windows.net",
            credential=self.account_key
        )

    def _save(self, name, content):
        ext = os.path.splitext(name)[1]
        name = f"{uuid.uuid4().hex}{ext}"

        blob_client = self.blob_service.get_blob_client(container=self.container_name, blob=name)
        blob_client.upload_blob(content, overwrite=False)
        return name

    def delete(self, name):
        """Видаляє файл з контейнера"""
        blob_client = self.blob_service.get_blob_client(container=self.container_name, blob=name)
        try:
            blob_client.delete_blob()
        except ResourceNotFoundError:
            pass

    def exists(self, name):
        blob_client = self.blob_service.get_blob_client(container=self.container_name, blob=name)
        return blob_client.exists()

    def url(self, name):
        return f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{name}"

    def get_available_name(self, name, max_length=None):
        """Генерує унікальне ім'я файлу"""
        ext = os.path.splitext(name)[1]
        return f"{uuid.uuid4().hex}{ext}"


class AvatarStorage(AzureBaseStorage):
    container_name = "avatars"

class ProductStorage(AzureBaseStorage):
    container_name = "products"

class PromoStorage(AzureBaseStorage):
    container_name = "promos"
