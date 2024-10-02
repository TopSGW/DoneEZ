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

class CustomUserLoginView(APIView):
    permission_classes = []  # No authentication required for login

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            return Response({
                'user': CustomUserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(access_token),
            }, status=status.HTTP_200_OK)
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
class CustomUserView(APIView):
    permission_classes = [IsAuthenticated]  # Require JWT Authentication

    def get(self, request):
        # `user`: The authenticated user instance.
        user = request.user
        # Since no `data` parameter is provided, the serializer is in **read-only** mode (serialization).
        serializer = CustomUserSerializer(user)
        # When you access `serializer.data`, the serializer internally calls the `to_representation()` method for each field defined in the serializer.
        # **`to_representation()`**: This method converts the `user` instance into a Python dictionary of primitive data types.
        ###
            # - **Fields Processed:**
            # - All fields listed in `fields` under the `Meta` class of `CustomUserSerializer`:
            # - `'email'`
            # - `'first_name'`
            # - `'last_name'`
            # - `'is_customer'`
            # - `'is_mechanic'`
            # - `'customer_profile'`
            # - `'mechanic_profile'`
            # - `'is_active'`
        ###
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        serializer = CustomUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            # In your view, when you call `serializer.save()`, you're invoking the serializer's `save()` method, which internally decides whether to call `create()` or `update()` based on whether an instance is provided.
            # - **Parameters:**
            # - `instance=user`: Indicates that an existing user is being updated.
            # - `data=request.data`: New data to update the user with.
            # - `partial=True`: Allows partial updates.
            # Since an `instance` is provided, `serializer.save()` will call the serializer's `update()` method.
            user = serializer.save()
            return Response(CustomUserSerializer(user).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# User Registration View
class CustomUserRegistrationView(APIView):
    permission_classes = []  # No authentication required for registration

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            return Response({
                'user': CustomUserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# Mechanic View
class MechanicProfileView(generics.RetrieveAPIView):
    queryset = MechanicProfile.objects.all()
    serializer_class = MechanicProfileSerializer

# CustomerProfile View
class CustomerProfileView(generics.RetrieveAPIView):
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerProfileSerializer