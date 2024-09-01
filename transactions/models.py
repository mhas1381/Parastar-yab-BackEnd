from django.db import models
from accounts.models.profiles import NurseProfile
from nurse_request.models import Request


class Transaction(models.Model):
    '''Temperary model for transactions in faze one.'''
    mode_choices = (
        ('+', 'پرداخت'),
        ('-', 'تسویه')
    )
    nurse_reqeust = models.OneToOneField(Request, on_delete=models.CASCADE, related_name='tarnsaction', null=True)
    nurse = models.ForeignKey(NurseProfile, on_delete=models.CASCADE, related_name='transactions')
    created_date = models.DateTimeField(auto_now_add=True)
    amount = models.FloatField()
    mode = models.CharField(default='+', choices=mode_choices, max_length=32)


    def __str__(self):
        '''String representation for transactions.'''
        return f'{self.nurse}->{self.mode}{self.amount}'
    
    @classmethod
    def payment(cls, request):
        '''Making a record of payment'''
        print(request)
        instace = Transaction.objects.create(
            nurse=request.nurse, 
            amount=request.duration_hours*request.nurse.salary_per_hour,
            mode='+',
            nurse_reqeust=request
        )
        instace.save()
        return instace
    

    @classmethod
    def checkout(cls, nurse):
        '''Making a record of payment'''
        print('checkout')
        instace = Transaction.objects.create(
            nurse=nurse, 
            amount=nurse.balance,
            mode='-'
        )
        instace.save()
        return instace