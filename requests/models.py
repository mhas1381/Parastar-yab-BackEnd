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

    CATEGORY_CHOICES = [
        ('CHILD', 'Child'),
        ('ELDERLY', 'Elderly'),
    ]

    client = models.ForeignKey(
        ClientProfile, on_delete=models.CASCADE, related_name='requests')
    nurse = models.ForeignKey(NurseProfile, on_delete=models.SET_NULL,
                              null=True, blank=True, related_name='requests')
    created_date = models.DateTimeField(auto_now_add=True)
    request_for_date = models.DateTimeField()
    request_start = models.DateTimeField()
    duration_hours = models.FloatField(
        validators=[MinValueValidator(0.0)],
        default=1.0,
        help_text="Duration in hours for which the nurse is needed"
    )
    request_end = models.DateTimeField()

    address = models.TextField()

    for_others = models.BooleanField(default=False)
    other_person_name = models.CharField(max_length=255, blank=True, null=True)
    other_person_phone_number = models.CharField(
        max_length=11, blank=True, null=True)

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='PENDING')
    rate = models.FloatField(validators=[MinValueValidator(
        0.0), MaxValueValidator(10.0)], null=True, blank=True)

    category = models.CharField(
        max_length=10, choices=CATEGORY_CHOICES, default='CHILD')

    def __str__(self):
        return f"Request {self.id} by {self.client.user.phone_number}"

    def clean(self):
        super().clean()
        if self.for_others:
            if not self.other_person_name or not self.other_person_phone_number:
                raise ValidationError(
                    "Both other person name and phone number must be provided if 'for others' is checked.")
        if self.duration_hours <= 0:
            raise ValidationError("Duration must be greater than 0 hours.")

    class Meta:
        ordering = ['-created_date']
