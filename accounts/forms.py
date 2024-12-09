from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, PasswordChangeForm
from .models import User
from django import forms
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import password_validation
from django.utils.translation import gettext_lazy as _

# class CustomUserCreationForm(UserCreationForm):
#     """
#     Enhanced user creation form
#     """
#     class Meta:
#         model = User
#         fields = (
#             'email', 
#             'first_name', 
#             'last_name', 
#             'phone_number', 
#             'user_type'
#         )

#     def clean_email(self):
#         """
#         Validate email uniqueness
#         """
#         email = self.cleaned_data['email']
#         try:
#             User.objects.get(email=email)
#             raise forms.ValidationError("A user with this email already exists.")
#         except User.DoesNotExist:
#             return email
        
class CustomUserCreationForm(UserCreationForm):
    backup_phone_number = forms.CharField(required=False)
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = (
            'email', 
            'first_name', 
            'last_name', 
            'phone_number', 
            'backup_phone_number',
            'profile_picture',
            'user_type'
        )

    phone_number = forms.CharField(
        label="Phone Number",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number with country code (e.g., +6471234567)',
        }),
        help_text="Include the '+' and country code before your number.",
    )

    backup_phone_number = forms.CharField(
        label="Backup Phone Number",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter backup phone number with country code (e.g., +6471234567)',
        }),
        help_text="Optional. Include the '+' and country code before your number.",
    )

    def clean_phone_number(self):
        """
        Validate primary phone number format.
        """
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.startswith('+'):
            raise forms.ValidationError("Phone number must start with '+'.")
        return phone_number

    def clean_backup_phone_number(self):
        """
        Validate backup phone number format if provided.
        """
        backup_phone_number = self.cleaned_data.get('backup_phone_number')
        if backup_phone_number and not backup_phone_number.startswith('+'):
            raise forms.ValidationError("Backup phone number must start with '+'.")
        return backup_phone_number
    

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get('backup_phone_number'):
            user.backup_phone_number = self.cleaned_data['backup_phone_number']
        if self.cleaned_data.get('profile_picture'):
            user.profile_picture = self.cleaned_data['profile_picture']
        
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """
    Custom login form with additional validation
    """
    username = forms.EmailField(
        widget=forms.TextInput(attrs={
            'autofocus': True, 
            'placeholder': 'Email Address'
        })
    )

    def confirm_login_allowed(self, user):
        """
        Additional login restrictions
        """
        if not user.is_active:
            raise forms.ValidationError(
                "This account is not active.",
                code='inactive',
            )
        if not user.is_verified:
            raise forms.ValidationError(
                "This account is not verified. Please contact support.",
                code='unverified',
            )
        


class CustomSetPasswordForm(forms.Form):
    """
    Custom form for resetting the user's password.
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput,
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_("Confirm new password"),
        strip=False,
        widget=forms.PasswordInput,
    )

    def __init__(self, user, *args, **kwargs):
        """
        Initialize the form with the user object.
        """
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_new_password1(self):
        """
        Validate the first password field against the password validation rules.
        """
        password1 = self.cleaned_data.get('new_password1')
        password_validation.validate_password(password1, self.user)
        return password1

    def clean_new_password2(self):
        """
        Ensure both password fields match.
        """
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        """
        Save the new password for the user.
        """
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user



class ForgotPasswordForm(forms.Form):
    """
    Form to collect the user's email for password reset.
    """
    email = forms.EmailField(
        label="Email Address",
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
    )



class ChangePasswordForm(PasswordChangeForm):
    """
    Custom form for changing the user's password.
    """
    old_password = forms.CharField(
        label="Old Password",
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter old password'}),
    )
    new_password1 = forms.CharField(
        label="New Password",
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter new password'}),
        help_text="Your password must be strong and meet the complexity requirements.",
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'}),
    )



class ContactUsForm(forms.Form):
    name = forms.CharField(
        label="Your Name",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your name'}),
    )
    email = forms.EmailField(
        label="Your Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
    )
    message = forms.CharField(
        label="Message",
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your message here'}),
    )
