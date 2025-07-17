from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import render

from google.oauth2 import id_token
from google.auth.transport import requests

GOOGLE_CLIENT_ID = "тут_твоїй_client_id"

@api_view(['POST'])
def register(request):
    try:
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if not username or not email or not password:
            return Response({'error': 'Всі поля обов’язкові'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Користувач вже існує'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        return Response({'message': 'Користувача зареєстровано'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    else:
        return Response({'error': 'Неправильні дані'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def google_login(request):
    token = request.data.get('id_token')
    if not token:
        return Response({'error': 'ID token is required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
        google_user_id = idinfo['sub']
        email = idinfo.get('email')
        name = idinfo.get('name', '')

        if not email:
            return Response({'error': 'Email not available'}, status=status.HTTP_400_BAD_REQUEST)

        user, created = User.objects.get_or_create(username=email, defaults={'email': email, 'first_name': name})

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'created': created
        })
    except ValueError:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


def custom_login(request):
    return render(request, 'authorization/login.html')

