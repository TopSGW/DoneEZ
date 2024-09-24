from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, MechanicProfileView, CustomerProfileView, QuoteRequestView, EstimateView, AppointmentView, PaymentView, CustomTokenObtainPairView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('mechanic-profile/<int:pk>/', MechanicProfileView.as_view(), name='mechanic_profile'),
    path('customer-profile/<int:pk>/', CustomerProfileView.as_view(), name='customer_profile'),
    path('quote-requests/', QuoteRequestView.as_view(), name='quote_requests'),
    path('estimates/', EstimateView.as_view(), name='estimates'),
    path('appointments/', AppointmentView.as_view(), name='appointments'),
    path('payments/', PaymentView.as_view(), name='payments'),
]
