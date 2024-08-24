from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import NurseProfile

# Create your views here.


class NurseRatingView(APIView):
    def get(self, request, nurse_id):
        try:
            nurse = NurseProfile.objects.get(id=nurse_id)
            average_rating = nurse.calculate_average_rating()
            return Response(
                {"average_rating": average_rating}, status=status.HTTP_200_OK
            )
        except NurseProfile.DoesNotExist:
            return Response(
                {"error": "Nurse not found"}, status=status.HTTP_404_NOT_FOUND
            )
