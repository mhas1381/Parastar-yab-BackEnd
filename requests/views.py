"""
views for request app
"""
from accounts.models.profiles import NurseProfile, ClientProfile
from accounts.models.users import User
from rest_framework.views import APIView
from .serializers import RequestSerializer, NurseListSerializer
from .models import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .permissions import IsClient, IsNurse



class ClientRequestAPIView(APIView):
    """Client side requests api views"""
    permission_classes = [IsAuthenticated, IsClient]


    def get(self, request, *args, **kwargs):
        """Getting all in proccess requests"""
        in_proccess_requests = Request.objects.filter(
            status__in=['PENDING', 'CLINET_CONFIRMATION', 'ACCEPTED', 'NURSING', ]
        ) 
        client = ClientProfile.objects.filter(user=request.user)

        in_proccess_requests = in_proccess_requests.filter(client=client)
        
        serializer = RequestSerializer(in_proccess_requests, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def post(self, request, *args, **kwargs):
        """Adding new request."""
        serializer = RequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'message':'data has problems'}, status=status.HTTP_400_BAD_REQUEST)

        clinet_profile = ClientProfile.objects.filter(user=request.user).first()
        if not clinet_profile:
            return Response({'message':'data has problems'}, status=status.HTTP_400_BAD_REQUEST)
        
        payload = {
            'client': clinet_profile
        }
        serializer.save(**payload)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    
    def put(self, request, pk=None, *args, **kwargs):
        """"""
        pass



class ClientFinishedRequests(APIView):
    '''Get requests that are finished.'''
    permission_classes = [IsAuthenticated, IsClient]


    def get(self, request, *args, **kwargs):
        '''List all finished requests.'''
        finished_requests = Request.objects.filter(status__in=['REJECTED', 'CANCELLED', 'COMPLETED']) 
        finished_requests = finished_requests.filter(client=request.user)

        serializer = RequestSerializer(finished_requests, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def get_details(self, request, pk=None, *args, **kwargs):
        '''Get a request with all details.'''
        finished_request = Request.objects.filter(pk=pk).first()

        if not finished_request:
            return Response({'message':'your data has problems'}, status=status.HTTP_400_BAD_REQUEST)
        

        Client = ClientProfile.objects.filter(user=request.user).first()
        if not Client: 
            return Response({'message':'your data has problems'}, status=status.HTTP_400_BAD_REQUEST)
        
        if finished_request.client == Client:
            serilizer = RequestSerializer(finished_request)
            return Response(serilizer.data, status=status.HTTP_200_OK)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)
        



class NurseList(APIView):
    """Getting all nurses not working right now"""
    permission_classes = [IsAuthenticated, IsClient]


    def get(self, request, *args, **kwargs):
        
        available_nurses = NurseProfile.objects.filter(is_working=False).order_by('-rate').values_list(
            'user__first_name',
            'user__last_name',
            'rate'
        )
        serializer = NurseListSerializer(available_nurses, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)



class NurseRequestsAPIView(APIView):
    """Nurses requests apiview"""
    permission_classes = [IsAuthenticated, IsNurse]

    def get(self, request, pk=None, *args, **kwargs):
        """Get list of nurse requests that are not finished or rejected"""
        if pk:
            return self.get_object(request, pk) 

        nurse_profile = NurseProfile.objects.filter(user=request.user).first()
        if not nurse_profile:
            return Response({'message': 'nurse profile did not fount'}, status=status.HTTP_400_BAD_REQUEST)
         
        on_going_requests = Request.objects.filter(
            status__in=['PENDING','CLINET_CONFIRMATION',  'ACCEPTED', 'NURSING'],
            nurse=nurse_profile 
            )
        
        serializer = RequestSerializer(on_going_requests, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def get_object(self, request, pk):
        '''Returning request with details'''

        nurse_profile = NurseProfile.objects.filter(user=request.user).first()
        if not nurse_profile:
            return Response({'message': 'nurse profile did not fount'}, status=status.HTTP_400_BAD_REQUEST)

        on_going_request = Request.objects.filter(
            status__in=['PENDING','CLINET_CONFIRMATION', 'ACCEPTED', 'NURSING'],
            nurse=nurse_profile,
            id=pk 
            )
        
        serializer = RequestSerializer(on_going_request)

        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def put(self, request, *args, **kwargs):
        """Changing status of a request"""



class NurseFinishedRequests(APIView):
    '''Nurse Requests wich they are completed or rejected.'''
    permission_classes = [IsAuthenticated, IsNurse]

    def get(self, request, pk=None, *args, **kwargs):
        '''List all finished requests.'''
        if pk:
            return self.get_object(request, pk)
        
        nurse_profile = NurseProfile.objects.filter(user=request.user).first()
        if not nurse_profile:
            return Response({'message': 'nurse profile did not fount'}, status=status.HTTP_400_BAD_REQUEST)
        
        finished_requests = Request.objects.filter(
            status__in=['COMPLETED', 'REJECTED'],
            nurse=nurse_profile 
        )

        serializer = RequestSerializer(finished_requests, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def get(self, request, pk):
        '''Get on request with details'''
        nurse_profile = NurseProfile.objects.filter(user=request.user).first()
        if not nurse_profile:
            return Response({'message': 'nurse profile did not fount'}, status=status.HTTP_400_BAD_REQUEST)
        
        finished_request = Request.objects.filter(
            status__in=[ 'COMPLETED', 'REJECTED'],
            nurse=nurse_profile,
            id=pk 
        )

        serializer = RequestSerializer(finished_request)

        return Response(serializer.data, status=status.HTTP_200_OK)
    

    



