from django.apps import AppConfig
import cloudinary
from decouple import config


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        # Configure Cloudinary only once the app is ready
        cloudinary.config(
            cloud_name=config('CLOUD_NAME'),
            api_key=config("API_KEY"),
            api_secret=config("API_SECRET"),
        )
