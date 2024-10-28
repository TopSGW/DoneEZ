from django.urls import path
from .views import (
    CustomUserLoginView,
    MechanicProfileView,     
    CustomUserRegistrationView, 
    MechanicDistanceFilterView, 
    StaffUserLoginView, 
    StaffUserRegistrationView,
    SuperUserRegistrationView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', CustomUserRegistrationView.as_view(), name='register'),
    path('login/', CustomUserLoginView.as_view(), name='login'),
    path('staff/login/', StaffUserLoginView.as_view(), name='staff-login'),
    path('staff/register/', StaffUserRegistrationView.as_view(), name='staff-register'),
    path('superuser/register', SuperUserRegistrationView.as_view(), name='superuser-register'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('mechanic-profile/<int:id>/', MechanicProfileView.as_view(), name='mechanic-profile'),
    path('mechanics/distance-filter/', MechanicDistanceFilterView.as_view(), name='mechanic_distance_filter')
]