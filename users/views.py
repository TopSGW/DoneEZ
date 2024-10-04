from django.shortcuts import render
from decouple import config
import requests

# Create your views here.
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model, authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny                                                                                                                                                                                                                                                                                                                                                                                                                                       

from .models import MechanicProfile, CustomerProfile, CustomUser
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

GOOGLE_API_KEY = config('GOOGLE_API_KEY')

def get_coordinates_from_zip(zip_code):
    """
    Get latitude and longitude from zip code using Google Geocoding API.
    """
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={zip_code}&key={GOOGLE_API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    if data['status'] == 'OK':
        # Extract latitude and longitude
        location = data['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    else:
        raise ValueError(f"Geocoding failed for {zip_code} with status {data['status']}")

def calculate_distance(customer_zip, mechanic_zip):
    """
    Calculate the distance between two zip codes using Google Distance Matrix API.
    """
    customer_coords = get_coordinates_from_zip(customer_zip)
    mechanic_coords = get_coordinates_from_zip(mechanic_zip)

    distance_matrix_url = (
        f"https://maps.googleapis.com/maps/api/distancematrix/json?"
        f"origins={customer_coords[0]},{customer_coords[1]}&"
        f"destinations={mechanic_coords[0]},{mechanic_coords[1]}&"
        f"key={GOOGLE_API_KEY}&units=imperial"
    )

    response = requests.get(distance_matrix_url)
    data = response.json()

    if data['status'] == 'OK':
        distance_text = data['rows'][0]['elements'][0]['distance']['text']
        duration_text = data['rows'][0]['elements'][0]['duration']['text']
        return {
            'distance': distance_text,  # e.g., "5.1 miles"
            'duration': duration_text   # e.g., "12 mins"
        }
    else:
        raise ValueError(f"Distance calculation failed with status {data['status']}")

# Method: GET
# URL: /mechanics/distance-filter/?customer_zip=08518&max_distance=15
class MechanicDistanceFilterView(generics.ListAPIView):
    """
    ListAPIView for filtering mechanic profiles by a specified distance range.
    """
    serializer_class = MechanicProfileSerializer

    def get_queryset(self):
        """
        Override the get_queryset method to filter mechanics based on distance.
        """
        customer_zip = self.request.query_params.get('customer_zip')  # Get customer zip from query params
        max_distance = float(self.request.query_params.get('max_distance', 10))  # Default max distance is 10 miles

        mechanics = MechanicProfile.objects.all()
        filtered_mechanics = []

        for mechanic in mechanics:
            mechanic_zip = mechanic.zip_code
            try:
                # Calculate distance between customer and mechanic zip codes
                distance_data = calculate_distance(customer_zip, mechanic_zip)
                distance_in_miles = float(distance_data['distance'].replace(' miles', ''))
                
                # Add mechanic to the list if within the specified distance range
                if distance_in_miles <= max_distance:
                    filtered_mechanics.append(mechanic)
            except ValueError:
                continue  # Skip mechanics if distance calculation fails

        return filtered_mechanics

    def list(self, request, *args, **kwargs):
        """
        Override the list method to return filtered mechanics within the distance range.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)    