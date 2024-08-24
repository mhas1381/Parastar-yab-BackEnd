from django.urls import path
from .views import NurseRatingView

urlpatterns = [
    path('nurse/<int:nurse_id>/rating/', NurseRatingView.as_view(), name='nurse-rating'),
]
