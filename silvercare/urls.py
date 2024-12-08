"""
URL configuration for silvercare project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from accounts.views import DashboardView, Base1View, TestMail, ContactUsView


from django.views.generic import TemplateView

class PrivacyPolicyView(TemplateView):
    template_name = 'privacy_policy.html'

class TermsOfServiceView(TemplateView):
    template_name = 'terms_of_service.html'


urlpatterns = [
    path("admin/", admin.site.urls),
    path('', DashboardView.as_view(), name='home'),
    path('base1/', Base1View.as_view(), name='base1'),
    path('test-mail/', TestMail.as_view(), name='testmail'),
    path('accounts/', include('accounts.urls')),
    path('tasks/', include('eldertasks.urls')),



    path('privacy-policy/', PrivacyPolicyView.as_view(), name='privacy-policy'),
    path('terms-of-service/', TermsOfServiceView.as_view(), name='terms-of-service'),
    path('contact-us/', ContactUsView.as_view(), name='contact-us'),

]
