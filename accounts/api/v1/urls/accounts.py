from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from rest_framework import routers
from ..views import *

router = routers.DefaultRouter()
# router.register(r'user-register', RegisterView, basename='user-register')
router.register(r'verify-otp', VerifyPhoneOTPView, basename='verify-otp')
router.register(r'update-user', UserUpdateView, basename='update-user')

urlpatterns = [
    path('', include(router.urls)),
    path('get-login-otp-mobile/<str:phone_number>/', ValidatePhoneSendOTP.as_view(), name='get-login-otp-mobile'),
    path('get-login-otp-mobile/<str:phone_number>/<str:role>/', ValidatePhoneSendOTP.as_view(), name='get-login-otp-mobile-with-role'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('jwt/create/', CustomTokenObtainPairView.as_view(), name='jwt-create'),
    path('jwt/refresh/', TokenRefreshView.as_view(), name='jwt-refresh'),
    path('jwt/verify/', TokenVerifyView.as_view(), name='jwt-verify'),
]
