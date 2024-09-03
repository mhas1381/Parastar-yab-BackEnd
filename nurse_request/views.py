"""
views for request app
"""
from accounts.models.profiles import NurseProfile, ClientProfile
from accounts.models.users import User
from rest_framework.views import APIView
from .serializers import RequestSerializer, NurseListSerializer, RequestSerializerExtra
from .models import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .permissions import IsClient, IsNurse


class NurseSetSallary(APIView):
    """Nurses setting salary or changing it."""

    permission_classes = [IsNurse, IsAuthenticated]

    def put(self, request, *args, **kwargs):
        """Changing the nurse salary."""
        user = User.objects.filter(pk=request.user.id).first()
        nurse = NurseProfile.objects.filter(user=user).first()

        nurse.salary_per_hour = request.data["salary_per_hour"]
        nurse.save()


        return Response({'salary': nurse.salary_per_hour}, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        """Getting nurse salary."""
        user = User.objects.filter(pk=request.user.id).first()
        nurse = NurseProfile.objects.filter(user=user).values(
            "user__first_name", 
            "user__last_name", 
            "salary_per_hour"
        ).first()

        return Response({'salary': nurse}, status=status.HTTP_200_OK)


class ClientRequestAPIView(APIView):
    """Client side requests api views"""

    permission_classes = [IsAuthenticated, IsClient]

    def get(self, request, pk=None, *args, **kwargs):
        """Getting all in proccess requests"""
        if pk:
            return self.get_object(request, pk)

        client = ClientProfile.objects.filter(user=request.user).first()
        in_proccess_requests = Request.objects.filter(
            status__in=["PENDING", "PAYMENT", "CLINET_CONFIRMATION", "ACCEPTED", "NURSING"],
            client=client).values(
            'id',
            'client',
            'client__user__first_name',
            'client__user__last_name',
            'nurse',
            'nurse__user__first_name',
            'nurse__user__last_name',
            'created_date',
            'request_for_date',
            'request_start',
            'duration_hours',
            'request_end',
            'address',
            'latitude',
            'longitude',
            'for_others',
            'status',
            'rate',
            'category',
            'payment',
            'other_information'
        )

        if not in_proccess_requests:
            return Response({"meessage": "no request yet"}, status=status.HTTP_200_OK)
        
        serializer = RequestSerializerExtra(in_proccess_requests, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_object(self, request, pk):
        """Get one of the requests wich is in proccess with details"""
        client = ClientProfile.objects.filter(user=request.user).first()
        in_proccess_requests = Request.objects.filter(
            status__in=[
                "PENDING",
                "CLINET_CONFIRMATION",
                "PAYMENT",
                "ACCEPTED",
                "NURSING",
            ],
            client=client,
            id=pk,
        ).values(
            'id',
            'client',
            'client__user__first_name',
            'client__user__last_name',
            'nurse',
            'nurse__user__first_name',
            'nurse__user__last_name',
            'created_date',
            'request_for_date',
            'request_start',
            'duration_hours',
            'request_end',
            'address',
            'latitude',
            'longitude',
            'for_others',
            'status',
            'rate',
            'category',
            'payment',
            'other_information'
        ).first()
        if not in_proccess_requests:
            return Response({'message': 'no request with this id'})

        serializer = RequestSerializerExtra(in_proccess_requests)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """Adding new request."""
        clinet_profile = ClientProfile.objects.filter(user=request.user).first()
        if not clinet_profile:
            return Response(
               status=status.HTTP_401_UNAUTHORIZED 
            )

        nurse_profile = NurseProfile.objects.filter(id=request.data['nurse']).first()
        if not nurse_profile:
            return Response(
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payload = {
            'client': clinet_profile,
        }
        payload.update(request.data)
        payload["nurse"] = nurse_profile
        payload["payment"] = request.data['duration_hours']*nurse_profile.salary_per_hour

        new_request = Request.objects.create(**payload)
        serializer = RequestSerializer(new_request)

        return Response(serializer.data, status=status.HTTP_201_CREATED)



    def put(self, request, pk=None, *args, **kwargs):
        """Changing the situation of the requests."""
        user_profile = ClientProfile.objects.filter(user=request.user).first()
        request_object = Request.objects.filter(client=user_profile, id=pk).first()
        if not request_object:
            return Response(
                {"message": "you dont have any requests"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if request_object.update_status(request.data, request.user.role):

            serializer = RequestSerializer(request_object)
            return Response(serializer.data)

        return Response(status=status.HTTP_400_BAD_REQUEST)



class ClientFinishedRequests(APIView):
    """Get requests that are finished."""

    permission_classes = [IsAuthenticated, IsClient]

    def get(self, request, pk=None, *args, **kwargs):
        """List all finished requests."""
        if pk:
            return self.get_object(request, pk)

        client = ClientProfile.objects.filter(user=request.user).first()
        finished_requests = Request.objects.filter(
            status__in=["REJECTED", "CANCELLED", "COMPLETED"], client=client).values(
            'id',
            'client',
            'client__user__first_name',
            'client__user__last_name',
            'nurse',
            'nurse__user__first_name',
            'nurse__user__last_name',
            'created_date',
            'request_for_date',
            'request_start',
            'duration_hours',
            'request_end',
            'address',
            'latitude',
            'longitude',
            'for_others',
            'status',
            'rate',
            'category',
            'payment',
            'other_information'
        )

        if not finished_requests:
            return Response({'message':'no finished requests.'})
        
        serializer = RequestSerializerExtra(finished_requests, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_object(self, request, pk):
        """Get a request with all details."""
        client = ClientProfile.objects.filter(user=request.user).first()
        finished_requests = Request.objects.filter(
            status__in=["REJECTED", "CANCELLED", "COMPLETED"], client=client, id=pk
        ).values(
            'id',
            'client',
            'client__user__first_name',
            'client__user__last_name',
            'nurse',
            'nurse__user__first_name',
            'nurse__user__last_name',
            'created_date',
            'request_for_date',
            'request_start',
            'duration_hours',
            'request_end',
            'address',
            'latitude',
            'longitude',
            'for_others',
            'status',
            'rate',
            'category',
            'payment',
            'other_information'
        ).first()

        if not finished_requests:
            return Response({'message':'no finished requests.'})
        
        serializer = RequestSerializerExtra(finished_requests)

        return Response(serializer.data, status=status.HTTP_200_OK)



class NurseList(APIView):
    """Getting all nurses not working right now"""

    permission_classes = [IsAuthenticated, IsClient]

    def get(self, request, *args, **kwargs):
        available_nurses = NurseProfile.objects.filter(is_working=False).order_by("-average_rate").values(
                "id", 
                "user__first_name", 
                "user__last_name", 
                "average_rate",
                "salary_per_hour"
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
            return Response(
                {"message": "nurse profile did not fount"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        on_going_requests = Request.objects.filter(
            status__in=["PENDING", "PAYMENT", "CLINET_CONFIRMATION", "ACCEPTED", "NURSING"],
            nurse=nurse_profile,
        ).values(
            'id',
            'client',
            'client__user__first_name',
            'client__user__last_name',
            'nurse',
            'nurse__user__first_name',
            'nurse__user__last_name',
            'created_date',
            'request_for_date',
            'request_start',
            'duration_hours',
            'request_end',
            'address',
            'latitude',
            'longitude',
            'for_others',
            'status',
            'rate',
            'category',
            'payment',
            'other_information'
        )
        if not on_going_requests:
            return Response({'message':'no requests yet.'})

        serializer = RequestSerializerExtra(on_going_requests, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_object(self, request, pk):
        """Returning request with details"""

        nurse_profile = NurseProfile.objects.filter(user=request.user).first()
        if not nurse_profile:
            return Response(
                {"message": "nurse profile did not fount"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        on_going_request = Request.objects.filter(
            status__in=["PENDING", "PAYMENT", "CLINET_CONFIRMATION", "ACCEPTED", "NURSING"],
            nurse=nurse_profile,
            id=pk,
        ).values(
            'id',
            'client',
            'client__user__first_name',
            'client__user__last_name',
            'nurse',
            'nurse__user__first_name',
            'nurse__user__last_name',
            'created_date',
            'request_for_date',
            'request_start',
            'duration_hours',
            'request_end',
            'address',
            'latitude',
            'longitude',
            'for_others',
            'status',
            'rate',
            'category',
            'payment',
            'other_information'
        ).first()

        serializer = RequestSerializerExtra(on_going_request)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk=None, *args, **kwargs):
        """Changing the situation of the requests."""
        nurse_profile = NurseProfile.objects.filter(user=request.user).first()
        request_object = Request.objects.filter(nurse=nurse_profile, id=pk).first()

        if not request_object:
            return Response({'message':'reqeust id is wrong'}, status=status.HTTP_400_BAD_REQUEST)
        
        if request_object.update_status(request.data, request.user.role):
            serializer = RequestSerializer(request_object)
            return Response(serializer.data)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class NurseFinishedRequests(APIView):
    """Nurse Requests wich they are completed or rejected."""

    permission_classes = [IsAuthenticated, IsNurse]

    def get(self, request, pk=None, *args, **kwargs):
        """List all finished requests."""
        if pk:
            return self.get_object(request, pk)

        nurse_profile = NurseProfile.objects.filter(user=request.user).first()
        if not nurse_profile:
            return Response(
                {"message": "nurse profile did not fount"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        finished_requests = Request.objects.filter(
            status__in=["COMPLETED", "REJECTED"], nurse=nurse_profile
        ).values(
            'id',
            'client',
            'client__user__first_name',
            'client__user__last_name',
            'nurse',
            'nurse__user__first_name',
            'nurse__user__last_name',
            'created_date',
            'request_for_date',
            'request_start',
            'duration_hours',
            'request_end',
            'address',
            'latitude',
            'longitude',
            'for_others',
            'status',
            'rate',
            'category',
            'payment',
            'other_information'
        )
        

        if not finished_requests:
            return Response({'message':'no finished requests.'})

        serializer = RequestSerializerExtra(finished_requests, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_object(self, request, pk):
        """Get on request with details"""
        nurse_profile = NurseProfile.objects.filter(user=request.user).first()
        if not nurse_profile:
            return Response(
                {"message": "nurse profile not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        finished_request = Request.objects.filter(
            status__in=["COMPLETED", "REJECTED"], nurse=nurse_profile, id=pk
        ).values(
            'id',
            'client',
            'client__user__first_name',
            'client__user__last_name',
            'nurse',
            'nurse__user__first_name',
            'nurse__user__last_name',
            'created_date',
            'request_for_date',
            'request_start',
            'duration_hours',
            'request_end',
            'address',
            'latitude',
            'longitude',
            'for_others',
            'status',
            'rate',
            'category',
            'payment',
            'other_information'
        ).first()

        if not finished_request:
            return Response({'message':'no finished requests.'})
        
        serializer = RequestSerializerExtra(finished_request)

        return Response(serializer.data, status=status.HTTP_200_OK)


class TopNursesAPIView(APIView):
    def get(self, request):
        top_nurses = NurseProfile.objects.order_by('-average_rate')
        nurses_data = [
            {
                "id": nurse.user.id,
                "name": nurse.user.get_full_name(),  # Assuming your User model has a get_full_name method
                "average_rate": nurse.average_rate,
            }
            for nurse in top_nurses
        ]
        return Response(nurses_data, status=status.HTTP_200_OK)
    