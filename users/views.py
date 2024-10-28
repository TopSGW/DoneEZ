from django.shortcuts import render
from rest_framework import permissions

# Create your views here.
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model, authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from .utils import calculate_real_distance, calculate_straight_line_distance, get_coordinates_from_zip
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D  # For distance measurements
from .models import MechanicProfile, CustomerProfile, CustomUser
from .permissions import IsSuperUser

from .serializers import (
    CustomUserSerializer, 
    UserRegistrationSerializer, 
    MechanicProfileSerializer, 
    MechanicProfileBasicSerializer,
    CustomerProfileSerializer,
    StaffUserRegistrationSerializer,
    SuperUserRegistrationSerializer,
)

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
        #  users = CustomUser.objects.all()
        #  Since no `data` parameter is provided, the serializer is in **read-only** mode (serialization).
        serializer = CustomUserSerializer(user)
        #  Pass `many=True` to the serializer to handle multiple instances
        #  serializer = CustomUserSerializer(users, many=True)
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

class SuperUserRegistrationView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = SuperUserRegistrationSerializer
    permission_classes = [IsSuperUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        return Response({
            'user': CustomUserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(access_token),
        }, status=status.HTTP_201_CREATED)

class StaffUserRegistrationView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = StaffUserRegistrationSerializer
    permission_classes = [IsSuperUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        return Response({
            'user': CustomUserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(access_token),
        }, status=status.HTTP_201_CREATED)
class StaffUserLoginView(APIView):
    permission_classes = []

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)
        if user and user.is_staff:
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            return Response({
                'user': CustomUserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(access_token),
            }, status=status.HTTP_200_OK)
        return Response({'detail': 'Invalid credentials or not a staff user'}, status=status.HTTP_401_UNAUTHORIZED)


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
        print(serializer._errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# Mechanic View
class MechanicProfileView(generics.RetrieveAPIView):
    permission_classes = []
    queryset = MechanicProfile.objects.all()
    serializer_class = MechanicProfileBasicSerializer
    lookup_field = 'id'  # Add this line

# CustomerProfile View
class CustomerProfileView(generics.RetrieveAPIView):
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerProfileSerializer

# Use a local database for zip codes to avoid API calls
# def get_coordinates_from_zip(zip_code):
#     """
#     Get latitude and longitude from zip code using a local database or cache.
#     """
#     # Assuming you have a model or a data structure that maps zip codes to coordinates
#     try:
#         location = ZipCode.objects.get(code=zip_code)
#         return location.latitude, location.longitude
#     except ZipCode.DoesNotExist:
#         raise ValidationError(f"Invalid zip code: {zip_code}")
    
# Method: GET
# URL: /mechanics/distance-filter/?customer_zip=08518&max_distance=15
class MechanicDistanceFilterView(generics.ListAPIView):
    permission_classes = []
    serializer_class = MechanicProfileSerializer

    def get_queryset(self):
        customer_zip = self.request.query_params.get('customer_zip')
        max_distance = float(self.request.query_params.get('max_distance', 25))  # Default to 25 miles

        if not customer_zip:
            raise ValidationError("Customer zip code is required.")

        # Use a local database or cache to get coordinates from zip code
        customer_lat, customer_lng = get_coordinates_from_zip(customer_zip)
        customer_location = Point(customer_lng, customer_lat, srid=4326)  # Note: longitude first

        max_distance_in_meters = max_distance * 1609.34  # Convert miles to meters

        mechanics = MechanicProfile.objects.filter(
            location__distance_lte=(customer_location, D(m=max_distance_in_meters))
        ).annotate(
            distance=Distance('location', customer_location)
        ).order_by('distance')

        return mechanics

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
