"""
chat_intermediary URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from chatbot.views import StartNewConversation, ContinueConversation, ConversationHistory

@login_required
def protected_view(request):
    return JsonResponse({'message': 'User is authenticated'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('protected-endpoint/', protected_view),
    path('start-conversation/', StartNewConversation.as_view(), name='start_conversation'),
    path('continue-conversation/', ContinueConversation.as_view(), name='continue_conversation'),
    path('conversation-history/', ConversationHistory.as_view(), name='conversation_history'),
]
