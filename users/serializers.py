from rest_framework import serializers, exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model, authenticate
from .models import MechanicProfile, CustomerProfile, CustomUser

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
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

class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = ['phone_number', 'address', 'zip_code', 'vehicle_make', 'vehicle_model', 'vehicle_year', 'vehicle_mileage']

class MechanicProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MechanicProfile
        fields = ['shop_name', 'rating', 'years_of_experience', 'phone_number', 'address', 'zip_code', 'certifications', 'is_mobile']

class CustomUserSerializer(serializers.ModelSerializer):
    is_customer = serializers.BooleanField(required=True)
    is_mechanic = serializers.BooleanField(required=True)

    customer_profile = CustomerProfileSerializer(required=False)  # Nested serializer
    mechanic_profile = MechanicProfileSerializer(required=False)  # Nested serializer

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'first_name', 'last_name', 'is_customer', 'is_mechanic', 'customer_profile', 'mechanic_profile']

    def create(self, validated_data):
        is_customer = validated_data.pop('is_customer')
        is_mechanic = validated_data.pop('is_mechanic')

        # Create the user
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            is_customer=is_customer,
            is_mechanic=is_mechanic
        )

        # Create profiles based on the flags
        if is_customer and 'customer_profile' in validated_data:
            customer_data = validated_data.pop('customer_profile')
            CustomerProfile.objects.create(user=user, **customer_data)

        if is_mechanic and 'mechanic_profile' in validated_data:
            mechanic_data = validated_data.pop('mechanic_profile')
            MechanicProfile.objects.create(user=user, **mechanic_data)

        return user

    def update(self, instance, validated_data):
        is_customer = validated_data.pop('is_customer')
        is_mechanic = validated_data.pop('is_mechanic')

        # Update the user fields
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.is_customer = is_customer
        instance.is_mechanic = is_mechanic
        instance.save()

        # Update customer profile if the flag is true
        if is_customer and 'customer_profile' in validated_data:
            customer_data = validated_data.pop('customer_profile')
            customer_profile, created = CustomerProfile.objects.get_or_create(user=instance)
            for attr, value in customer_data.items():
                setattr(customer_profile, attr, value)
            customer_profile.save()

        # Update mechanic profile if the flag is true
        if is_mechanic and 'mechanic_profile' in validated_data:
            mechanic_data = validated_data.pop('mechanic_profile')
            mechanic_profile, created = MechanicProfile.objects.get_or_create(user=instance)
            for attr, value in mechanic_data.items():
                setattr(mechanic_profile, attr, value)
            mechanic_profile.save()

        return instance

class UserRegistrationSerializer(serializers.ModelSerializer):
    is_customer = serializers.BooleanField(required=True)
    is_mechanic = serializers.BooleanField(required=True)
    customer_profile = CustomerProfileSerializer(required=False)  
    mechanic_profile = MechanicProfileSerializer(required=False)

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'first_name', 'last_name', 'is_customer', 'is_mechanic', 'customer_profile', 'mechanic_profile']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        is_customer = validated_data.pop('is_customer')
        is_mechanic = validated_data.pop('is_mechanic')

    # Create the user
        try:
            user = CustomUser.objects.create_user(
                email=validated_data['email'],
                password=validated_data['password'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                is_customer=is_customer,
                is_mechanic=is_mechanic
            )
            print("User created:", user)
        except Exception as e:
            print(f"Error while creating user: {e}")  # Print the error
            raise
        # Create profiles based on flags
        if is_customer:
            customer_data = validated_data.get('customer_profile')
            if customer_data:
                try:
                    CustomerProfile.objects.create(user=user, **customer_data)
                except Exception as e:
                    print(f"Error while creating customer_profile: {e}")

        if is_mechanic:
            mechanic_data = validated_data.get('mechanic_profile')
            print(mechanic_data)
            if mechanic_data:
                try:
                    MechanicProfile.objects.create(user=user, **mechanic_data)
                except Exception as e:
                    print(f"Error while creating mechanic_profile: {e}")

        return user