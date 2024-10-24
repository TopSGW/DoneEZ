from rest_framework import serializers, exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model, authenticate
from .models import MechanicProfile, CustomerProfile, CustomUser

User = get_user_model()

class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = ['phone_number', 'zip_code', 'address']

class MechanicProfileSerializer(serializers.ModelSerializer):
    distance = serializers.SerializerMethodField()
    class Meta:
        model = MechanicProfile
        fields = ['business_name', 'job_title', 'web_site', 'business_info', 'heard_info', 'rating', 'availability', 'years_of_experience', 'phone_number', 'address', 'zip_code', 'certifications', 'is_mobile',
                  'address_city', 'address_state', 'map_verified', 'address_latitude', 'address_longitude', 'distance']
        
    def get_distance(self, obj):
        # Return the distance in miles, rounded to two decimal places
        return round(obj.distance.mi, 2)    

class CustomUserSerializer(serializers.ModelSerializer):
    is_customer = serializers.BooleanField(required=True)
    is_mechanic = serializers.BooleanField(required=True)
    customer_profile = CustomerProfileSerializer(required=False)
    mechanic_profile = MechanicProfileSerializer(required=False)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    class Meta:
        model = CustomUser
        fields = [
            'email', 'password', 'first_name', 'last_name',
            'is_customer', 'is_mechanic', 'customer_profile',
            'mechanic_profile', 'is_active'
        ]
        extra_kwargs = {
            'is_active': {'read_only': True},
        }

    def create(self, validated_data):
        is_customer = validated_data.pop('is_customer')
        is_mechanic = validated_data.pop('is_mechanic')
        customer_profile_data = validated_data.pop('customer_profile', None)
        mechanic_profile_data = validated_data.pop('mechanic_profile', None)
        password = validated_data.pop('password')
        with transaction.atomic():
            user = CustomUser.objects.create(
                email=validated_data['email'],
                first_name=validated_data.get('first_name', ''),
                last_name=validated_data.get('last_name', ''),
                is_customer=is_customer,
                is_mechanic=is_mechanic,
            )
            user.set_password(password)
            user.save()

            if is_customer and customer_profile_data:
                CustomerProfile.objects.create(user=user, **customer_profile_data)

            if is_mechanic and mechanic_profile_data:
                try:
                    MechanicProfile.objects.create(user=user, **mechanic_profile_data)
                except Exception as e:
                    print(e)

        return user

    def update(self, instance, validated_data):
        is_customer = validated_data.get('is_customer', instance.is_customer)
        is_mechanic = validated_data.get('is_mechanic', instance.is_mechanic)
        customer_profile_data = validated_data.pop('customer_profile', None)
        mechanic_profile_data = validated_data.pop('mechanic_profile', None)

        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.is_customer = is_customer
        instance.is_mechanic = is_mechanic

        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)

        instance.save()

        if is_customer and customer_profile_data:
            CustomerProfile.objects.update_or_create(
                user=instance,
                defaults=customer_profile_data
            )

        if is_mechanic and mechanic_profile_data:
            MechanicProfile.objects.update_or_create(
                user=instance,
                defaults=mechanic_profile_data
            )

        return instance

class StaffUserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'first_name', 'last_name']
    
    def create(self, validated_data):
        user = CustomUser.objects.create_staffuser(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        return user

class SuperUserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'first_name', 'last_name']
    
    def create(self, validated_data):
        user = CustomUser.objects.create_superuser(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        return user
    
class UserRegistrationSerializer(serializers.ModelSerializer):
    is_customer = serializers.BooleanField(required=True)
    is_mechanic = serializers.BooleanField(required=True)
    customer_profile = CustomerProfileSerializer(required=False)
    mechanic_profile = MechanicProfileSerializer(required=False)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    class Meta:
        model = CustomUser
        fields = [
            'email', 'password', 'first_name', 'last_name', 'is_customer',
            'is_mechanic', 'customer_profile', 'mechanic_profile'
        ]
    def create(self, validated_data):
        # Reuse the create method from CustomUserSerializer
        serializer = CustomUserSerializer(data=validated_data)
        serializer.is_valid(raise_exception=True)
        return serializer.save()