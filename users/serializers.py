from rest_framework import serializers, exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model, authenticate
from .models import MechanicProfile, CustomerProfile, QuoteRequest, Estimate, Appointment, Payment, Service

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the username field from the serializer
        self.fields.pop('username', None)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            # Authenticate the user using the custom backend
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if not user:
                raise serializers.ValidationError(_('No active account found with the given credentials'))
        else:
            raise serializers.ValidationError(_('Must include "email" and "password"'))

        # Generate JWT tokens
        refresh = self.get_token(user)

        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        return data

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'password2', 'first_name', 'last_name']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

# Serializer for the MechanicProfile
class MechanicProfileSerializer(serializers.ModelSerializer):
    user = RegisterSerializer()

    class Meta:
        model = MechanicProfile
        fields = ['user', 'services', 'operation_hours', 'location', 'experience', 'is_mobile']

# Serializer for the CustomerProfile
class CustomerProfileSerializer(serializers.ModelSerializer):
    user = RegisterSerializer()

    class Meta:
        model = CustomerProfile
        fields = ['user', 'vehicle_info']

# Serializer for Service
class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['category', 'name', 'description']

# Serializer for QuoteRequest
class QuoteRequestSerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True)

    class Meta:
        model = QuoteRequest
        fields = ['customer', 'services', 'vehicle_info', 'preferred_time', 'additional_notes', 'status', 'created_at']

# Serializer for Estimate
class EstimateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estimate
        fields = ['quote_request', 'mechanic', 'price_estimate', 'service_time_estimate', 'additional_notes', 'created_at']

# Serializer for Appointment
class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['estimate', 'appointment_time', 'location', 'status']

# Serializer for Payment
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['appointment', 'deposit_amount', 'final_payment_amount', 'payment_status', 'payment_method', 'created_at']
