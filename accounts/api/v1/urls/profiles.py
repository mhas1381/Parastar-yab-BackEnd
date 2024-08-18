from django.urls import path,include
from rest_framework.routers import DefaultRouter
from ..views import ClientProfileViewSet, NurseProfileViewSet

router = DefaultRouter()
router.register(r'client_profiles', ClientProfileViewSet)
router.register(r'nurse_profiles', NurseProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
]