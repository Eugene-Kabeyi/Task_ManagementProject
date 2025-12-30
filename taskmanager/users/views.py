from django.shortcuts import render
from rest_framework import generics, permissions, status
from .serializers import UserSerializer, RegisterUserSerializer, LoginUserSerializer
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model

class RegisterUserView(generics.CreateAPIView):
    """View to register a new user."""
    queryset = get_user_model().objects.all() # Required for CreateAPIView
    serializer_class = RegisterUserSerializer # Serializer to handle user registration
    permission_classes = [permissions.AllowAny] # Allow anyone to access this view
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data) # Get serializer with request data
        serializer.is_valid(raise_exception=True) # Validate the data   
        user = serializer.save() # Save the new user instance
        
        # Create token for the user
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'User created successfully'
        }, status=status.HTTP_201_CREATED)

class LoginUserView(APIView):
    """View to log in a user."""
    permission_classes = [permissions.AllowAny] # Allow anyone to access this view

    # Handle POST request for user login
    def post(self, request, *args, **kwargs):
        serializer = LoginUserSerializer(data=request.data) # Serializer to handle login data
        serializer.is_valid(raise_exception=True) # Validate the data
        username = serializer.validated_data['username'] # Get username from validated data
        password = serializer.validated_data['password'] # Get password from validated data
        user = authenticate(request, username=username, password=password) # Authenticate user
        
        # If authentication is successful, log in the user and return token
        if user is not None:
            login(request, user)
            # Create or get token for the user
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "user": UserSerializer(user).data,
                "token": token.key
            }, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutUserView(APIView):
    """View to log out a user."""
    permission_classes = [permissions.IsAuthenticated] # Only authenticated users can access this view

    # Handle POST request for user logout
    def post(self, request, *args, **kwargs):
        try:
            request.user.auth_token.delete() # Delete the user's token
            logout(request) # Log out the user
        except:
            pass
        logout(request) # Log out the user
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
    
class UserProfileView(generics.RetrieveUpdateAPIView):
    """View to retrieve and update user profile."""
    queryset = get_user_model().objects.all() # Required for RetrieveUpdateAPIView
    serializer_class = UserSerializer # Serializer to handle user data
    permission_classes = [permissions.IsAuthenticated] # Only authenticated users can access this view

    def get_object(self):
        return self.request.user # Return the currently authenticated user
    