from django.urls import path
from .views import (
    AccountVerificationView,
    PasswordResetConfirmView,
    UserRegistrationView,
    CustomLoginView,
    CustomLogoutView,
    ForgotPasswordView,
)


urlpatterns = [

    path('auth/register/', 
         UserRegistrationView.as_view(), 
         name='register'),
    path('auth/login/', 
         CustomLoginView.as_view(), 
         name='login'),
    path('auth/logout/', 
         CustomLogoutView.as_view(), 
         name='logout'),
    path('auth/verify/<uidb64>/<token>/', 
         AccountVerificationView.as_view(), 
         name='verify_account'),
    path('auth/reset/<uidb64>/<token>/', 
         PasswordResetConfirmView.as_view(), 
         name='password_reset_confirm'),
    path('auth/forgot-password/',
          ForgotPasswordView.as_view(),
            name='forgot-password'),
]