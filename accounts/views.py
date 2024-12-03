from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy, reverse
# Create your views here.
# from django.contrib.auth.forms import SetPasswordForm
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from eldertasks.models import Notification
from django.contrib.auth import views as auth_views
from django.views.generic import CreateView, View
from django.utils.encoding import force_str, force_bytes
from django .utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.urls import path
from .utils import AccountVerificationService
from .models import User
from .forms import (
    CustomUserCreationForm, 
    CustomAuthenticationForm, 
    CustomSetPasswordForm,
    ForgotPasswordForm
)

class UserRegistrationView(CreateView):
    """
    Comprehensive user registration view
    """
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        """
        Additional processing on successful form submission
        """
        response = super().form_valid(form)
        
        user = self.object
        try:
            AccountVerificationService.send_verification_email(user)
            messages.success(self.request, "A verification email has been sent to your email address.")
        except Exception as e:
            messages.error(self.request, f"Error sending verification email: {e}")


        Notification.create_notification(
            user=self.object,
            message="Welcome to Silvercare! Complete your profile to get started.",
            notification_type=Notification.NotificationType.SYSTEM
        )
        
        return response
    
    def form_invalid(self, form):
        """
        Add custom behavior on form submission failure.
        """
        messages.error(self.request, "There was an error in your registration. Please correct the errors below.")
        return super().form_invalid(form)




class CustomLoginView(auth_views.LoginView):
    """
    Enhanced login view with additional features
    """
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    redirect_field_name = 'next'
    redirect_to = reverse_lazy('home')

    def form_valid(self, form):
        # This method is called when the form is successfully validated.
        user = form.get_user()
        messages.success(self.request, f"Welcome back, {user.first_name}!")
        return super().form_valid(form)

    def form_invalid(self, form):
        # This method is called when the form validation fails.
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form)



class CustomLogoutView(auth_views.LogoutView):
    """
    Customized logout view
    """
    next_page = 'login'




class AccountVerificationView(View):
    """
    View to handle account verification
    """
    def get(self, request, uidb64, token):
        try:
            # Decode user ID
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if default_token_generator.check_token(user, token):
                # Verify the user
                user.is_verified = True
                user.save()
                
                messages.success(
                    request, 
                    "Your account has been successfully verified!"
                )
                return redirect('login')
            
            else:
                messages.error(
                    request, 
                    "Verification link is invalid or has expired."
                )
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            messages.error(
                request, 
                "Invalid verification link."
            )
        
        return redirect('login')
    


class ForgotPasswordView(View):
    """
    View to handle forgotten password requests.
    """
    template_name = 'forgot_password.html'
    form_class = ForgotPasswordForm

    def get(self, request):
        """
        Render the password reset request form.
        """
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """
        Handle the password reset request.
        """
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email).first()
            if user:
                # Generate password reset token and UID
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))

                # Generate reset link
                reset_link = request.build_absolute_uri(
                    reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                )

                # Send reset email
                self.send_password_reset_email(email, reset_link)

                messages.success(
                    request, "An email has been sent to reset your password. Please check your inbox."
                )
                return redirect('login')
            else:
                messages.error(request, "No user found with that email address.")
        return render(request, self.template_name, {'form': form})



class PasswordResetConfirmView(View):
    """
    View to handle password reset confirmation
    """
    def get(self, request, uidb64, token):
        try:
            # Decode user ID
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            
            # Check token validity
            if default_token_generator.check_token(user, token):
                # Render password reset form
                form = CustomSetPasswordForm(user)
                return render(request, 'password_reset_confirm.html', {
                    'form': form,
                    'uidb64': uidb64,
                    'token': token
                })
            else:
                messages.error(
                    request, 
                    "Password reset link is invalid or has expired."
                )
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            messages.error(
                request, 
                "Invalid password reset link."
            )
        
        return redirect('login')
    

    def post(self, request, uidb64, token):
        try:
            # Decode user ID
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            
            # Check token validity
            if default_token_generator.check_token(user, token):
                # Process password reset form
                form = CustomSetPasswordForm(user, request.POST)
                if form.is_valid():
                    form.save()
                    messages.success(
                        request, 
                        "Your password has been reset successfully!"
                    )
                    return redirect('login')
                else:
                    return render(request, 'password_reset_confirm.html', {
                        'form': form,
                        'uidb64': uidb64,
                        'token': token
                    })
            else:
                messages.error(
                    request, 
                    "Password reset link is invalid or has expired."
                )
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            messages.error(
                request, 
                "Invalid password reset link."
            )
        
        return redirect('login')
    




class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Dashboard view for authenticated users.
    """
    template_name = 'accounts/dashboard.html'

    def get_context_data(self, **kwargs):
        """
        Add any additional context if needed.
        """
        context = super().get_context_data(**kwargs)
        context['welcome_message'] = f"Welcome, {self.request.user.username}!"
        return context
