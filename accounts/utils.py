import uuid
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from .models import User
from django.template.loader import render_to_string


class AccountVerificationService:
    """
    Service class to handle user account verification
    """
    @classmethod
    def send_verification_email(cls, user):
        """
        Generate and send account verification email
        """
        # Generate verification token
        token = default_token_generator.make_token(user)
        
        # Encode user ID
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Construct verification link
        verification_link = reverse('verify_account', kwargs={
            'uidb64': uid, 
            'token': token
        })
        
        # Full URL (assuming you have a domain in settings)
        full_verification_link = f"{settings.SITE_DOMAIN}{verification_link}"

        subject = "Welcome to SILVERCARE"
        sender = settings.EMAIL_HOST_USER 
        recipients = [user.email]
        context = {
            'full_name' : user.first_name,
            'user_email': user.email,
            'verification_url': full_verification_link,
        }
        message = render_to_string('account-verify.html', context)
        html_message = render_to_string('account-verify.html',context)

        send_mail(subject=subject ,
                   message=message,
                   from_email=sender,
                   recipient_list=recipients,
                   html_message=html_message)




class PasswordResetService:
    """
    Service class to handle password reset functionality
    """
    @classmethod
    def send_password_reset_email(cls, user):
        """
        Generate and send password reset email
        """
        # Generate reset token
        token = default_token_generator.make_token(user)
        
        # Encode user ID
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_link = reverse('password_reset_confirm', kwargs={
            'uidb64': uid, 
            'token': token
        })
        
        # Full URL 
        full_reset_link = f"{settings.SITE_DOMAIN}{reset_link}"
        subject = "Password Reset Request"
        sender = settings.EMAIL_HOST_USER
        recipients = [user.email]
        context = {
            'full_name' : user.first_name,
            'user_email': user.email,
            'reset_link': full_reset_link,
        }
        message = render_to_string('password_reset_email.html', context)
        html_message = render_to_string('password_reset_email.html',context)

        send_mail(subject=subject ,
                   message=message,
                   from_email=sender,
                   recipient_list=recipients,
                   html_message=html_message)
        