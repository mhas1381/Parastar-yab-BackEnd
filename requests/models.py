from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.dispatch import receiver
from django.db.models.signals import post_save
from accounts.models import ClientProfile, NurseProfile


class Request(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('NURSING', 'Nursing'),
    ]

    client = models.ForeignKey(
        ClientProfile, on_delete=models.CASCADE, related_name='requests')
    nurse = models.ForeignKey(NurseProfile, on_delete=models.SET_NULL,
                              null=True, blank=True, related_name='requests')
    created_date = models.DateTimeField(auto_now_add=True)
    request_for_date = models.DateTimeField()
    request_start = models.DateTimeField()
    request_end = models.DateTimeField()

    address = models.TextField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    for_others = models.BooleanField(default=False)
    other_person_name = models.CharField(max_length=255, blank=True, null=True)
    other_person_phone_number = models.CharField(
        max_length=11, blank=True, null=True)

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='PENDING')
    rate = models.FloatField(validators=[MinValueValidator(
        0.0), MaxValueValidator(10.0)], null=True, blank=True)
    comment = models.TextField(blank=True)

    def __str__(self):
        return f"Request {self.id} by {self.client.user.phone_number}"


    def clean(self):
            super().clean()
            if self.for_others:
                if not self.other_person_name or not self.other_person_phone_number:
                    raise ValidationError(
                        "Both other person name and phone number must be provided if 'for others' is checked.")
    class Meta:
        ordering = ['-created_date']
