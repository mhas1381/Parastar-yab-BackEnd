from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from accounts.models import ClientProfile, NurseProfile
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import NurseProfile

# from .models import Request


class Request(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "در انتظار"),
        ("ACCEPTED", "پذیرفته شده"),
        ("REJECTED", "رد شده"),
        ("COMPLETED", "تکمیل شده"),
        ("CANCELLED", "لغو شده"),
        ("PAYMENT", "پرداخت"),
        ("CLINET_CONFIRMATION", "انتظار برای تایید متقاضی"),
        ("NURSING", "پرستاری در حال انجام"),
    ]

    CATEGORY_CHOICES = [
        ("CHILD", "فرزند خردسال"),
        ("ELDERLY", "والدین کهنسال"),
    ]

    client = models.ForeignKey(
        ClientProfile, on_delete=models.CASCADE, related_name="requests"
    )
    nurse = models.ForeignKey(
        NurseProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requests",
    )
    created_date = models.DateTimeField(auto_now_add=True)
    request_for_date = models.DateTimeField(null=True, blank=True)
    request_start = models.DateTimeField(null=True, blank=True)
    duration_hours = models.FloatField(
        validators=[MinValueValidator(0.0)],
        default=1.0,
        help_text="مدت زمان درخواست به ساعت",
    )
    request_end = models.DateTimeField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    for_others = models.BooleanField(default=False)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    rate = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        null=True,
        blank=True,
    )

    category = models.CharField(
        max_length=10, choices=CATEGORY_CHOICES, default="CHILD"
    )
    payment = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"درخواست {self.id} توسط {self.client.user.phone_number}"

    def clean(self):
        super().clean()
        if self.duration_hours <= 0:
            raise ValidationError("مدت زمان باید بیشتر از 0 ساعت باشد.")

    def update_status(self, user_request, role):
        """Changing the status based on the role and the previous status."""
        print(self.status)
        print(user_request['status'])
        print(role)
        if user_request['status'] == "ACCEPTED" and role == "NURSE" and self.status == "PENDING":
            nurse = self.nurse
            nurse.is_working = True
            nurse.save()

            other_pending_request = Request.objects.filter(
                nurse=nurse,
                status="PENDING",
            ).exclude(id=self.id)

            for request in other_pending_request:
                request.status = "REJECTED"
                request.save()

            self.status = "ACCEPTED"
            self.save()
            return True

        elif user_request['status'] == "REJECTED" and role == "NURSE" and self.status == "PENDING":
            self.status = "REJECTED"
            self.save()
            return True

        elif user_request['status'] == "CANCELLED" and role == "CLIENT" and self.status == "PENDING":
            self.status = "CANCELLED"
            self.save()
            return True

        elif user_request['status'] == "NURSING" and role == "NURSE" and self.status == "ACCEPTED":
            self.status = "NURSING"
            self.save()
            return True

        elif user_request['status'] == "PAYMENT" and role == "NURSE" and self.status == "NURSING":
            self.status = "PAYMENT"
            self.save()
            return True

        elif user_request['status'] == "CLINET_CONFIRMATION" and role == "CLIENT" and self.status == 'PAYMENT':
            self.status = "CLINET_CONFIRMATION"
            self.save()

            from transactions.models import  Transaction
            Transaction.payment(self)
            
            self.status = "CLINET_CONFIRMATION"
            self.save()
            
            return True

        elif user_request['status'] == "COMPLETED" and role == "CLIENT" and self.status == "CLINET_CONFIRMATION":
            # Set the rate if provided
            if user_request['rate'] is not None:
                self.rate = user_request['rate']
            else:
                raise ValidationError("Rate must be provided before completing the request.")

            # Update the status to COMPLETED
            self.status = "COMPLETED"
            self.save()

            nurse = self.nurse
            nurse.is_working = False
            nurse.save()

            return True
        print('kikika')
        return False

        
    class Meta:
        ordering = ["-created_date"]


@receiver(post_save, sender=Request)
def update_nurse_average_rate(sender, instance, created, **kwargs):
    """
    This function updates the average rating for a nurse when a request is completed by a client.
    """
    if instance.status == "COMPLETED" and instance.rate:
        nurse = instance.nurse
        total_ratings = nurse.requests.filter(status="COMPLETED").count()
        total_sum = sum(request.rate for request in nurse.requests.filter(status="COMPLETED"))
        nurse.average_rate = round(total_sum / total_ratings) if total_ratings > 0 else 0.0
        nurse.save()