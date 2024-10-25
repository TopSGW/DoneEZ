from django.urls import path
from .views import SendMessageView

urlpatterns = [
    path('send-alert/', SendMessageView.as_view(), name='send-alert'),
]
