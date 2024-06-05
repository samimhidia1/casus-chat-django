from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import requests
from django.conf import settings
from .models import Conversation
import json

@method_decorator(csrf_exempt, name='dispatch')
class StartNewConversation(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        question = data.get('question')
        if not question:
            return JsonResponse({'error': 'Question is required'}, status=400)

        user = request.user

        # Forward the question to the langserve microservice
        try:
            response = requests.post(
                'https://casusragllmyqi6snyi-container-casus-rag-v3.functions.fnc.fr-par.scw.cloud/rag-conversation/invoke',
                json={'question': question}
            )
        except requests.RequestException as e:
            return JsonResponse({'error': f'Failed to connect to langserve microservice: {e}'}, status=500)

        if response.status_code == 200:
            conversation_data = response.json()
            # Save the conversation to the database
            conversation = Conversation.objects.create(
                user=user,
                conversation_id=conversation_data['conversation_id'],
                messages=conversation_data['messages']
            )
            return JsonResponse({'conversation_id': conversation.conversation_id, 'messages': conversation.messages})
        else:
            return JsonResponse({'error': 'Failed to start conversation'}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class ContinueConversation(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        conversation_id = data.get('conversation_id')
        question = data.get('question')
        if not conversation_id or not question:
            return JsonResponse({'error': 'Conversation ID and question are required'}, status=400)

        user = request.user

        try:
            conversation = Conversation.objects.get(conversation_id=conversation_id, user=user)
        except Conversation.DoesNotExist:
            return JsonResponse({'error': 'Conversation not found'}, status=404)

        # Forward the conversation data to the langserve microservice
        try:
            response = requests.post(
                'https://casusragllmyqi6snyi-container-casus-rag-v3.functions.fnc.fr-par.scw.cloud/rag-conversation/invoke',
                json={'conversation_id': conversation_id, 'question': question, 'messages': conversation.messages}
            )
        except requests.RequestException as e:
            return JsonResponse({'error': f'Failed to connect to langserve microservice: {e}'}, status=500)

        if response.status_code == 200:
            conversation_data = response.json()
            # Update the conversation in the database
            conversation.messages = conversation_data['messages']
            conversation.save()
            return JsonResponse({'conversation_id': conversation.conversation_id, 'messages': conversation.messages})
        else:
            return JsonResponse({'error': 'Failed to continue conversation'}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class ConversationHistory(View):
    def get(self, request):
        user = request.user
        conversations = Conversation.objects.filter(user=user).order_by('-created_at')
        conversation_list = [
            {
                'conversation_id': conversation.conversation_id,
                'messages': conversation.messages,
                'created_at': conversation.created_at,
                'updated_at': conversation.updated_at
            }
            for conversation in conversations
        ]
        return JsonResponse({'conversations': conversation_list})
