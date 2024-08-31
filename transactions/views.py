'''
views for transactions
'''
from rest_framework.views import APIView
from django.db.models import Sum, Q, Count
from .models import Transaction
from accounts.models.profiles import NurseProfile 
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from nurse_request.permissions import IsNurse



class NurseCredentialsAPIView(APIView):
    '''Nurse credentials'''
    permission_classes = [IsAuthenticated, IsNurse]

    def get(self, reqeust, *args, **kwargs):
        '''Getting nurse balance.'''
        positive_transactoins = Transaction.objects.filter(mode='+').aggregate(Sum('amount'))['amount__sum'] 
        negative_transactoins = Transaction.objects.filter(mode='-').aggregate(Sum('amount'))['amount__sum']
        
        if not positive_transactoins:
            positive_transactoins = 0

        if not negative_transactoins:
            negative_transactoins = 0
        balance = positive_transactoins - negative_transactoins

        nurse = NurseProfile.objects.filter(user=reqeust.user).first()

        nurse.balance = balance
        nurse.save()

        return Response({'balance': nurse.balance})
    



class NurseCheckoutAPIView(APIView):
    '''checking out for nurse'''
    permission_classes = [IsAuthenticated, IsNurse]
    
    def get(self, reqeust, *args, **kwargs):
        '''Checkout nurse income.'''
        nurse = NurseProfile.objects.filter(user=reqeust.user).first()
        Transaction.checkout(nurse)

        return Response({'message': 'checkout was successfull'})


