from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
import uuid
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager
# Create your models here.
from cloudinary.models import CloudinaryField
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent



class User(AbstractUser):
    # USER_TYPE_CHOICES = [
    #     ('Elder', 'Elder'),
    #     ('Helper', 'Helper'),
    #     ('Admin', 'Admin'),
    # ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    last_name = models.CharField(max_length=100, null=False, blank=False)
    first_name = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(_('email address'), unique=True)

    phone_number = PhoneNumberField(
        unique=True,  # Ensure no duplicate phone numbers
        null=False,
        blank=False,
        help_text="Enter your phone number starting with the country code (e.g., +647...)."
    )
    backup_phone_number = PhoneNumberField(
        unique=False, 
        null=True,
        blank=True,
        help_text="Enter your phone number starting with the country code (e.g., +647...)."
    )

    profile_picture = CloudinaryField(
        'image', 
        blank=True, 
        null=True,
        help_text="Profile picture (Max 5MB, recommended 500x500px)",
        transformation={
            'width': 500,  # Standardize width
            'height': 500,  # Standardize height
            'crop': 'fill',  # Crop to fill
            'quality': 'auto:good',  # Automatic quality optimization
            'format': 'webp'  # Convert to WebP for smaller file size
        }
    )
    address = models.TextField(blank=True, null=True)
    # user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    is_verified = models.BooleanField(
        default=False,
        help_text="Account verification status"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    objects = CustomUserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['email', 'is_verified']),
            # models.Index(fields=['user_type'])
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    @property
    def name(self):
        """
        Convenient property to get full name
        """
        return self.get_full_name()

    @property
    def profile_picture_url(self):
        """
        Get profile picture URL with fallback
        """
        return (
            self.profile_picture.url if self.profile_picture 
            else "/static/img/hero.jpg"
        )

    # def is_elder(self):
    #     return self.user_type == 'Elder'


    # def is_helper(self):
    #     return self.user_type == 'Helper'
    
    def save(self, *args, **kwargs):
        """
        Custom save method for additional validations
        """
        # Ensure email is lowercase
        self.email = self.email.lower()
        
        # Set username to email for compatibility
        self.username = self.email
        
        super().save(*args, **kwargs)

   
