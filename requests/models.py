from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from accounts.models import ClientProfile, NurseProfile
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import NurseProfile
from .models import Request


class Rating(models.Model):
    nurse = models.ForeignKey(
        NurseProfile, on_delete=models.CASCADE, related_name="ratings"
    )
    request = models.ForeignKey(
        Request, on_delete=models.CASCADE, related_name="ratings"
    )
    rating = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    comment = models.TextField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating {self.rating} for {self.nurse.user.username}"


class Request(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "در انتظار"),
        ("ACCEPTED", "پذیرفته شده"),
        ("REJECTED", "رد شده"),
        ("COMPLETED", "تکمیل شده"),
        ("CANCELLED", "لغو شده"),
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
    request_for_date = models.DateTimeField()
    request_start = models.DateTimeField()
    duration_hours = models.FloatField(
        validators=[MinValueValidator(0.0)],
        default=1.0,
        help_text="مدت زمان درخواست به ساعت",
    )
    request_end = models.DateTimeField()
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

    def __str__(self):
        return f"درخواست {self.id} توسط {self.client.user.phone_number}"

    def clean(self):
        super().clean()
        if self.duration_hours <= 0:
            raise ValidationError("مدت زمان باید بیشتر از 0 ساعت باشد.")

    def update_status(self, status, role):
        """Changing the status based on the role and the previous status"""

        if status == "ACCEPTED" and role == "NURSE" and self.status == "PENDING":
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

        elif status == "REJECTED" and role == "NURSE" and self.status == "PENDING":
            self.status = "REJECTED"
            self.save()
            return True

        elif status == "CANCELLED" and role == "CLIENT" and self.status == "PENDING":
            self.status = "CANCELLED"
            self.save()
            return True

        elif status == "NURSING" and role == "NURSE" and self.status == "ACCEPTED":
            self.status = "NURSING"
            self.save()
            return True

        elif (
            status == "CLINET_CONFIRMATION"
            and role == "NURSE"
            and self.status == "NURSING"
        ):
            self.status = "CLINET_CONFIRMATION"
            self.save()
            return True

        elif (
            status == "COMPLETED"
            and role == "CLIENT"
            and self.status == "CLINET_CONFIRMATION"
        ):
            self.status = "COMPLETED"
            self.save()

            nurse = self.nurse
            nurse.is_working = False
            nurse.save()

            return True

        return False

    class Meta:
        ordering = ["-created_date"]
