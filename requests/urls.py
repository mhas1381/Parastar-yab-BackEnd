'''
mapping the urls for request app
'''
from django.urls import path
from requests.views import *


urlpatterns = [
    path('available/nurses/', NurseList.as_view(), name='available_nurses'),
    path('client/request/<int:pk>/', ClientRequestAPIView.as_view(), name='client_request_detail'),
    path('client/request/', ClientRequestAPIView.as_view(), name='client_request'), 
    path('client/request/history/<int:pk>/', ClientFinishedRequests.as_view(), name='finished_request_detail'),
    path('client/request/history/', ClientFinishedRequests.as_view(), name='finished_request'),
    path('nurse/request/<int:pk>/', NurseRequestsAPIView.as_view(), name='nurse_request_detail'),
    path('nurse/request/', NurseRequestsAPIView.as_view(), name='nurse_request'),
    path('nurse/request/history/<int:pk>/', NurseFinishedRequests.as_view(), name='nurse_request_history_detail'),
    path('nurse/request/history/', NurseFinishedRequests.as_view(), name='nurse_request_history'),
    path('nurse/salary/', NurseSetSallary.as_view(), name='nurse_salary')
]