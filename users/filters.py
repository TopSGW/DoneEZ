# your_app/filters.py

import django_filters
from .models import MechanicProfile
from rest_framework.exceptions import ValidationError
from django.db.models import Q


class MechanicProfileFilter(django_filters.FilterSet):
    business_name = django_filters.CharFilter(field_name='business_name', lookup_expr='icontains')
    business_info = django_filters.CharFilter(field_name='business_info', lookup_expr='icontains')
    heard_info = django_filters.CharFilter(field_name='heard_info', lookup_expr='icontains')
    job_title = django_filters.CharFilter(field_name='job_title', lookup_expr='icontains')
    rating_min = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    rating_max = django_filters.NumberFilter(field_name='rating', lookup_expr='lte')
    years_of_experience_min = django_filters.NumberFilter(field_name='years_of_experience', lookup_expr='gte')
    years_of_experience_max = django_filters.NumberFilter(field_name='years_of_experience', lookup_expr='lte')
    is_mobile = django_filters.BooleanFilter(field_name='is_mobile')
    verified = django_filters.BooleanFilter(field_name='verified')
    offered_services = django_filters.CharFilter(method='filter_offered_services')
    zip_code = django_filters.CharFilter(field_name='zip_code', lookup_expr='exact')
    address_city = django_filters.CharFilter(field_name='address_city', lookup_expr='icontains')
    address_state = django_filters.CharFilter(field_name='address_state', lookup_expr='icontains')

    # Availability Filters
    available_day = django_filters.CharFilter(method='filter_available_day')
    available_time = django_filters.CharFilter(method='filter_available_time')
    available_day_time = django_filters.CharFilter(method='filter_available_day_time')
    
    class Meta:
        model = MechanicProfile
        fields = [
            'business_name',
            'business_info',
            'heard_info',
            'job_title',
            'rating_min',
            'rating_max',
            'years_of_experience_min',
            'years_of_experience_max',
            'is_mobile',
            'verified',
            'offered_services',
            'zip_code',
            'address_city',
            'address_state',
            'available_day',
            'available_time',
            'available_day_time',
        ]
    
    def filter_offered_services(self, queryset, name, value):
        return queryset.filter(offered_services__icontains=value)
    
    def filter_available_day(self, queryset, name, value):
        """
        Filters mechanics who are available on the specified day.
        """
        valid_days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        value = value.lower()
        if value not in valid_days:
            raise ValidationError({name: f"Invalid day '{value}'. Must be one of {', '.join(valid_days)}."})
        # Ensure the list for the day has at least one time slot
        return queryset.filter(**{f'availability__{value}__len__gt': 0})
    
    def filter_available_time(self, queryset, name, value):
        """
        Filters mechanics who are available at the specified time on any day.
        The time should be in the format "HH-HH", e.g., "8-12".
        """
        if '-' not in value:
            raise ValidationError({name: "Invalid time format. Expected 'HH-HH'."})
        start_time, end_time = value.split('-', 1)
        try:
            start_time = int(start_time)
            end_time = int(end_time)
            if not (0 <= start_time < end_time <= 24):
                raise ValueError
        except ValueError:
            raise ValidationError({name: "Invalid time values. Hours should be integers between 0 and 24, and start_time < end_time."})
        # Use PostgreSQL's JSONB containment operator to check if any day contains the time_slot
        return queryset.filter(
            Q(availability__mon__contains=[value]) |
            Q(availability__tue__contains=[value]) |
            Q(availability__wed__contains=[value]) |
            Q(availability__thu__contains=[value]) |
            Q(availability__fri__contains=[value]) |
            Q(availability__sat__contains=[value]) |
            Q(availability__sun__contains=[value])
        )
    
    def filter_available_day_time(self, queryset, name, value):
        """
        Filters mechanics who are available on a specific day and time.
        The value should be in the format "day:HH-HH", e.g., "mon:8-12".
        """
        if ':' not in value:
            raise ValidationError({name: "Invalid format. Expected 'day:HH-HH'."})
        day, time_slot = value.split(':', 1)
        day = day.lower()
        valid_days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        if day not in valid_days:
            raise ValidationError({name: f"Invalid day '{day}'. Must be one of {', '.join(valid_days)}."})
        if '-' not in time_slot:
            raise ValidationError({name: "Invalid time format. Expected 'HH-HH'."})
        start_time, end_time = time_slot.split('-', 1)
        try:
            start_time = int(start_time)
            end_time = int(end_time)
            if not (0 <= start_time < end_time <= 24):
                raise ValueError
        except ValueError:
            raise ValidationError({name: "Invalid time values. Hours should be integers between 0 and 24, and start_time < end_time."})
        # Use PostgreSQL's JSONB containment operator to check if the specific day contains the time_slot
        return queryset.filter(**{f'availability__{day}__contains': [time_slot]})

