from django.urls import path
from .views import HouseListCreate, user, login_view, RegisterView, CreateBookingView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('user/', user, name='user'),
    path('login/', login_view, name='login'),
    path('houses/', HouseListCreate.as_view(), name='house-list-create'),
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('bookings/', CreateBookingView.as_view(), name='create-booking'),
]