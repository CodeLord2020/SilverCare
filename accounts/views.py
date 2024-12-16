from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy, reverse
# Create your views here.
# from django.contrib.auth.forms import SetPasswordForm
from django.views.generic import TemplateView
from django.db.models import Avg
from django.contrib.auth.mixins import LoginRequiredMixin
from eldertasks.models import Notification
from django.contrib.auth import views as auth_views
from django.contrib.auth import update_session_auth_hash
from django.views.generic import CreateView, View
from django.utils.encoding import force_str, force_bytes
from django .utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.urls import path
from django.http.response import HttpResponseForbidden
from django.template import engines
from .utils import AccountVerificationService, PasswordResetService
from django.contrib.auth.decorators import login_required
from eldertasks.models import Task, TaskApplication, Review
from django.contrib import auth
from .models import User
from .forms import (
    CustomUserCreationForm, 
    CustomAuthenticationForm, 
    CustomSetPasswordForm,
    ForgotPasswordForm,
    ChangePasswordForm,
    ContactUsForm,
    UserProfileForm
)

class UserRegistrationView(CreateView):
    """
    Comprehensive user registration view
    """
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['USER_TYPE_CHOICES'] = User.USER_TYPE_CHOICES
        return context

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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['page_topic'] = "CREATE ACCOUNT"
        return context
    
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
        for error in form.errors.get('__all__', []):
            if 'not verified' in error.lower():
                messages.warning(self.request, error)
            else:
                messages.error(self.request, "Invalid email or password. Please try again.")
        return super().form_invalid(form)



# class CustomLogoutView(auth_views.LogoutView):
#     """
#     Customized logout view
#     """
#     # next_page = 'login'

def logout(request):
    auth.logout(request)
    return redirect('login')



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
                return redirect('home')
            
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
    


@login_required
def profile_view(request, user_id):
    # Get user
    user = get_object_or_404(User, id=user_id)

    # Statistics
    profile_picture = user.profile_picture_url
    tasks_created_count = Task.objects.filter(elder=user).count()
    tasks_completed_count = Task.objects.filter(elder=user, status='Completed').count()
    tasks_applied_count = TaskApplication.objects.filter(helper=user).count()
    average_rating = Review.objects.filter(helper=user).aggregate(Avg('rating'))['rating__avg']

    # Handle form submission for profile update
    if request.method == 'POST':#and request.user == user:
        if request.user == user:
            # Check if a file was uploaded via the profile picture form
            if 'profile_picture' in request.FILES:
                user.profile_picture = request.FILES['profile_picture']
                user.save()
                return redirect('profile', user_id=user.id)

            # Handle full profile update
            form = UserProfileForm(request.POST, request.FILES, instance=user)
            if form.is_valid():
                form.save()
                return redirect('profile', user_id=user.id)
        else:
            return HttpResponseForbidden()
    else:
        form = UserProfileForm(instance=user)

    context = {
        'user': user,
        'profile_picture': profile_picture,
        'tasks_created_count': tasks_created_count,
        'tasks_completed_count': tasks_completed_count,
        'tasks_applied_count': tasks_applied_count if request.user == user else None,
        'average_rating': average_rating,
        'form': form,
    }

    return render(request, 'accounts/profile.html', context)



class ForgotPasswordView(View):
    """
    View to handle forgotten password requests.
    """
    template_name = 'accounts/forgot_password.html'
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
                PasswordResetService.send_password_reset_email(user=user)

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
                return render(request, 'accounts/password_reset_confirm.html', {
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
                    return render(request, 'accounts/password_reset_confirm.html', {
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
    

class ChangePasswordView(LoginRequiredMixin, View):
    """
    View to handle changing the user's password.
    """
    template_name = 'accounts/change_password.html'
    form_class = ChangePasswordForm

    def get(self, request):
        """
        Render the change password form.
        """
        form = self.form_class(user=request.user)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        """
        Handle the password change process.
        """
        form = self.form_class(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keeps the user logged in
            messages.success(request, "Your password was successfully updated!")
            return redirect('dashboard')  # Redirect to a desired page after success
        else:
            messages.error(request, "Please correct the error below.")
        return render(request, self.template_name, {'form': form})


class DashboardView(TemplateView):
    """ Dashboard view for authenticated users. """
    template_name = 'accounts/dashboard.html'

    def get_context_data(self, **kwargs):
        """ Add any additional context if needed. """
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_authenticated:
            context['welcome_message'] = f"Welcome, {self.request.user.first_name}!"
        else:
            context['welcome_message'] = "Welcome stranger!"
        
        context['page_topic'] = "DASHBOARD"

        return context


class Base1View(LoginRequiredMixin, TemplateView):
    """
    Dashboard view for authenticated users.
    """
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        """
        Add any additional context if needed.
        """
        context = super().get_context_data(**kwargs)
        context['welcome_message'] = f"Welcome, {self.request.user.first_name}!"
        return context
    

class TestMail(LoginRequiredMixin, TemplateView):
    """
    Dashboard view for authenticated users.
    """
    template_name = 'accounts/testmail.html'

    def get_context_data(self, **kwargs):
        """
        Add any additional context if needed.
        """
        context = super().get_context_data(**kwargs)
        context = {
            'full_name' : 'Rasheed',
            'user_email': 'brashed@gmaai.com',
            'verification_url': 'http://127.0.0.1:5000/test-mail/',
             'uidb64': 'hjjdjij',
             'token': 'jdshi874808bnw97ywu893yrrhi9'
        }
        context['welcome_message'] = f"Welcome, {self.request.user.first_name}!"
        return context
    



class ContactUsView(View):
    template_name = 'contact_us.html'
    form_class = ContactUsForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            
            # Render the email template
            django_engine = engines['django']
            email_content = django_engine.get_template('contact_us_email.html').render({
                'name': name,
                'email': email,
                'message': message,
            })

            # Send the email
            send_mail(
                subject=f"New Contact Us Message from {name}",
                message="This is an HTML email. Please view it as such.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['brasheed123@gmail.com'],
                html_message=email_content,
                fail_silently=False,
            )
            
            messages.success(request, "Your message has been sent successfully!")
            return redirect('contact-us')

        return render(request, self.template_name, {'form': form})
