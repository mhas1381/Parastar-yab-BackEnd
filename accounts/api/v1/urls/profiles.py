from django.urls import path,include
from ..views import CreateClientProfileApiView, CreateNurseProfileApiView

urlpatterns = [

    path('client-profile/', CreateClientProfileApiView.as_view(), name='create-client-profile'),
    path('nurse-profile/', CreateNurseProfileApiView.as_view(), name='create-nurse-profile'),

]