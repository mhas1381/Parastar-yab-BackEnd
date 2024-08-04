from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator
import re


class MyUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The phone_number field must be set')

        # Normalize phone number
        phone_number = self.normalize_phone_number(phone_number)

        # Check for existing user with the same phone number
        if self.model.objects.filter(phone_number=phone_number).exists():
            raise ValueError('این شماره موبایل قبلا ثبت شده است.')

        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, password, **extra_fields)

    def normalize_phone_number(self, phone_number):

        phone_number = re.sub(r'\D', '', phone_number)

        # seceond character should be checked
        if len(phone_number) == 11 and phone_number.startswith('0'):

            normalized_number = '+98' + phone_number
        elif len(phone_number) == 10 and phone_number.startswith('9'):

            normalized_number = '+98' + phone_number
        else:
            raise ValueError('شماره موبایل معتبر نمی باشد')

        return normalized_number


class User(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=15, unique=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    birthday = models.DateField(null=True , blank=True)
    national_id = models.CharField(
        max_length=10, unique=True, null=True, blank=True)
    avatar = models.ImageField(blank=True, null=True)
    national_card_image = models.ImageField(null=True, blank=True)

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        Client = "CLIENT", "Client"
        Nurse = "NURSE", "Nurse"

    role = models.CharField(
        max_length=50, choices=Role.choices, default=Role.ADMIN)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    objects = MyUserManager()

    def __str__(self):
        return self.phone_number


class ClientManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(role=User.Role.Client)


class Client(User):
    objects = ClientManager()

    class Meta:
        proxy = True

    def welcome(self):
        return "Only for Clients"


class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.phone_number}"


class NurseManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(role=User.Role.Nurse)


class Nurse(User):
    objects = NurseManager()

    class Meta:
        proxy = True

    def welcome(self):
        return "Only for Nurses"


class NurseProfile(models.Model):
    practical_auth_status = [
        ('UP', 'Upload documents'),
        ('R', 'Rejected'),
        ('S', 'Successful')
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nurse_id = models.IntegerField(null=True, blank=True)
    additional_info = models.TextField(null=True, blank=True)
    salary_per_hour = models.FloatField(null=True, blank=True)
    practical_auth = models.CharField(
        choices=practical_auth_status,
        default='UP',
        max_length=20
    )
    is_working = models.BooleanField(default=False)
    average_rate = models.FloatField(
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(10.0)
        ],
        default=0.0
    )

    def __str__(self):
        return f"{self.user.phone_number}"

# Signal handlers for creating profiles when a user is created
@receiver(post_save, sender=User)
def save_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == User.Role.Client:
            ClientProfile.objects.create(user=instance)
        elif instance.role == User.Role.Nurse:
            NurseProfile.objects.create(user=instance)
