from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from accounts.models import ClientProfile, NurseProfile


class Request(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'در انتظار'),
        ('ACCEPTED', 'پذیرفته شده'),
        ('REJECTED', 'رد شده'),
        ('COMPLETED', 'تکمیل شده'),
        ('CANCELLED', 'لغو شده'),
        ('NURSING', 'پرستاری در حال انجام'),
    ]

    CATEGORY_CHOICES = [
        ('CHILD', 'فرزند خردسال'),
        ('ELDERLY', 'والدین کهنسال'),
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
        help_text="مدت زمان درخواست به ساعت"
    )
    request_end = models.DateTimeField()

    address = models.TextField()

    for_others = models.BooleanField(default=False)

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='PENDING')
    rate = models.FloatField(validators=[MinValueValidator(
        0.0), MaxValueValidator(10.0)], null=True, blank=True)

    category = models.CharField(
        max_length=10, choices=CATEGORY_CHOICES, default='CHILD')

    def __str__(self):
        return f"درخواست {self.id} توسط {self.client.user.phone_number}"

    def clean(self):
        super().clean()
        if self.duration_hours <= 0:
            raise ValidationError("مدت زمان باید بیشتر از 0 ساعت باشد.")

    class Meta:
        ordering = ['-created_date']
