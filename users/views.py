from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model, authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny                                                                                                                                                                                                                                                                                                                                                                                                                                       

from .models import MechanicProfile, CustomerProfile
from .serializers import  CustomUserSerializer, UserRegistrationSerializer, MechanicProfileSerializer, CustomerProfileSerializer

User = get_user_model()

class LoginView(APIView):
    permission_classes = []
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'is_customer': user.is_customer,
                'is_mechanic': user.is_mechanic
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
class CustomUserView(APIView):
    permission_classes = [IsAuthenticated]  # Require JWT Authentication

    def get(self, request):
        # Get the profile of the authenticated user
        user = request.user  # JWT will provide the authenticated user
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)

    def put(self, request):
        user = request.user  # JWT will provide the authenticated user
        serializer = CustomUserSerializer(user, data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# User Registration View
class CustomUserRegistrationView(APIView):
    # Ensure the registration view does not have any authentication requirements
    permission_classes = []  # No authentication required for registration
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Mechanic View
class MechanicProfileView(generics.RetrieveAPIView):
    queryset = MechanicProfile.objects.all()
    serializer_class = MechanicProfileSerializer

# CustomerProfile View
class CustomerProfileView(generics.RetrieveAPIView):
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerProfileSerializer