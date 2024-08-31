'''
mapping the urls for request app
'''
from django.urls import path
from .views import *

urlpatterns = [
    path('nurse/balance/', NurseCredentialsAPIView.as_view(), name='nurse-balance'),
    path('nurse/checkout/', NurseCheckoutAPIView.as_view(), name='nurse-checkout')
]