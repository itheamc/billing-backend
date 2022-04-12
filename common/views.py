import re

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model

UserModel = get_user_model()


@csrf_exempt
@api_view(['POST'])
def register(request):
    password = request.data.get('password')
    c_password = request.data.get('c_password')

    if password is None or c_password is None:
        return Response(
            {'error': 'password and c_password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not password == c_password:
        return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

    if len(password) < 8:
        return Response({'error': 'Password must be at least 8 characters'}, status=status.HTTP_400_BAD_REQUEST)

    if not any(char.isdigit() for char in password):
        return Response({'error': 'Password must contain at least one number'}, status=status.HTTP_400_BAD_REQUEST)

    if not any(char.isupper() for char in password):
        return Response({'error': 'Password must contain at least one uppercase letter'},
                        status=status.HTTP_400_BAD_REQUEST)

    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

    email_regex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
    if not re.match(email_regex, email):
        return Response({'error': 'Email is invalid'}, status=status.HTTP_400_BAD_REQUEST)

    if UserModel.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

    # Validating the User's First Name
    first_name = request.data.get('first_name')
    if not first_name:
        return Response({'error': 'First name is required'}, status=status.HTTP_400_BAD_REQUEST)

    # Pop first_name, email, password, c_password from request.data
    request.data.pop('first_name')
    request.data.pop('email')
    request.data.pop('password')
    request.data.pop('c_password')

    user = UserModel.objects.create_user(email=email, password=password, first_name=first_name, **request.data)
    return Response({'message': 'User created successfully', 'user': user.as_dict}, status=status.HTTP_201_CREATED)
