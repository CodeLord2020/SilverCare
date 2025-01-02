
# messaging/urls.py
from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('inbox/', views.InboxView.as_view(), name='inbox'),
    path('conversation/<uuid:pk>/', 
         views.ConversationView.as_view(), 
         name='conversation'),
    path('search/', views.MessageSearchView.as_view(), name='search'),
]