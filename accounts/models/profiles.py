from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings  # برای استفاده از AUTH_USER_MODEL
from django.db.models import Avg


class ClientProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.phone_number}"


class NurseProfile(models.Model):
    practical_auth_status = [
        ("UP", "Upload documents"),
        ("R", "Rejected"),
        ("S", "Successful"),
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nurse_id = models.IntegerField(null=True, blank=True)
    additional_info = models.TextField(null=True, blank=True)
    salary_per_hour = models.FloatField(null=True, blank=True , default=100000)
    practical_auth = models.CharField(
        choices=practical_auth_status, default="UP", max_length=20
    )
    is_working = models.BooleanField(default=False)
    average_rate = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)], default=0.0
    )

    def calculate_average_rating(self):
        average = self.average_rate.aggregate(Avg("rating"))["rating__avg"]
        return average if average is not None else 0.0

    def __str__(self):
        return f"{self.user.phone_number}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == "CLIENT":
            ClientProfile.objects.create(user=instance)
        elif instance.role == "NURSE":
            NurseProfile.objects.create(user=instance)
