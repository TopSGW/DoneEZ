from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny                                                                                                                                                                                                                                                                                                                                                                                                                                       

from .models import MechanicProfile, CustomerProfile, QuoteRequest, Estimate, Appointment, Payment
from .serializers import RegisterSerializer, MechanicProfileSerializer, CustomerProfileSerializer, QuoteRequestSerializer, EstimateSerializer, AppointmentSerializer, PaymentSerializer, CustomTokenObtainPairSerializer

User = get_user_model()

# User Registration View
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

# MechanicProfile View
class MechanicProfileView(generics.RetrieveAPIView):
    queryset = MechanicProfile.objects.all()
    print(queryset.values())
    serializer_class = MechanicProfileSerializer

# CustomerProfile View
class CustomerProfileView(generics.RetrieveAPIView):
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerProfileSerializer

# QuoteRequest View
class QuoteRequestView(generics.ListCreateAPIView):
    queryset = QuoteRequest.objects.all()
    serializer_class = QuoteRequestSerializer

# Estimate View
class EstimateView(generics.ListCreateAPIView):
    queryset = Estimate.objects.all()
    serializer_class = EstimateSerializer

# Appointment View
class AppointmentView(generics.ListCreateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

# Payment View
class PaymentView(generics.ListCreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer