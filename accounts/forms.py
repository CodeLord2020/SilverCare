from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from .models import User
from django import forms
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import password_validation
from django.utils.translation import gettext_lazy as _

class CustomUserCreationForm(UserCreationForm):
    """
    Enhanced user creation form
    """
    class Meta:
        model = User
        fields = (
            'email', 
            'first_name', 
            'last_name', 
            'phone_number', 
            'user_type'
        )

    def clean_email(self):
        """
        Validate email uniqueness
        """
        email = self.cleaned_data['email']
        try:
            User.objects.get(email=email)
            raise forms.ValidationError("A user with this email already exists.")
        except User.DoesNotExist:
            return email
        


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
