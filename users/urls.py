from django.urls import path
from .views import CustomUserLoginView, CustomUserView, CustomUserRegistrationView, MechanicDistanceFilterView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', CustomUserRegistrationView.as_view(), name='register'),
    path('login/', CustomUserLoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', CustomUserView.as_view(), name='profile'),
    path('mechanics/distance-filter/', MechanicDistanceFilterView.as_view(), name='mechanic_distance_filter')
]