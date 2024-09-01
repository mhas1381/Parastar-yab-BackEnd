from rest_framework.response import Response
from rest_framework import viewsets, status,permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics
# from kavenegar import *
from .serializers import *
from .utils import otp_generator
from accounts.models import *
User = get_user_model()


def send_otp(phone_number):
    if phone_number:
        try:
            key = "1234"  # پیش‌فرض 1234 اگر کلید None باشد
            phone_number = str(phone_number)
            otp_key = str(key)
            print(f"Generated OTP: {otp_key}")  # For debugging purposes

            # این بخش مربوط به ارسال OTP با استفاده از Kavenegar است
            # api = KavenegarAPI(settings.KAVENEGAR_API_KEY)  # Replace with your Kavenegar API key
            # params = {
            #     'sender': settings.KAVENEGAR_SENDER,
            #     'receptor': phone_number,
            #     'message': f'Your OTP is: {otp_key}',
            # }
            # response = api.sms_send(params)
            # print(f"SMS Response: {response}")  # For debugging purposes

            return otp_key

        except Exception as e:
            print('there is otp problem')
            return False
    return False



class ValidatePhoneSendOTP(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # دریافت شماره تلفن و نقش از درخواست
            phone_number = request.data.get('phone_number')
            role = request.data.get('role', User.Role.CLIENT)  # به صورت پیش‌فرض CLIENT
            
            if phone_number:
                phone_number = str(phone_number).strip()

                # گرفتن یا ساختن کاربر بر اساس شماره تلفن
                user, created = User.objects.get_or_create(phone_number=phone_number)

                # اگر کاربر تازه ساخته شده است، نقش را تنظیم کنید
                if created:
                    user.role = role
                    user.save()
                
                # ارسال OTP و ذخیره‌ی زمان ارسال
                new_otp = send_otp(phone_number)
                if new_otp:
                    user.otp = new_otp
                    user.otp_created_at = timezone.now()
                    user.save()

                    return Response({
                        'message': 'OTP sent successfully',
                        'status': status.HTTP_200_OK,
                    })
                else:
                    return Response({
                        'message': 'Failed to send OTP',
                        'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    })
            else:
                return Response({
                    'message': 'Phone number is required',
                    'status': status.HTTP_400_BAD_REQUEST,
                })
        except Exception as e:
            return Response({
                'message': str(e),
                'status': status.HTTP_400_BAD_REQUEST,
            })

class VerifyPhoneOTPView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = VerifyPhoneOTPModelSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        otp = serializer.validated_data['otp']

        try:
            user = User.objects.get(phone_number__iexact=phone_number)

            # بررسی انقضای OTP
            if user.otp_created_at and timezone.now() > user.otp_created_at + timedelta(minutes=2):
                return Response({
                    'message': 'OTP has expired',
                    'status': status.HTTP_400_BAD_REQUEST,
                })

            # بررسی صحت OTP
            if user.otp == otp:
                # استفاده از توکن سفارشی
                token = CustomTokenObtainPairSerializer.get_token(user)

                # بررسی اینکه آیا کاربر پروفایل خود را کامل کرده است یا نه
                is_new = not all([user.first_name])

                response_data = {
                    'status': True,
                    'details': 'Login Successfully',
                    'token': {
                        'refresh': str(token),
                        'access': str(token.access_token),
                        'role': token['role'],  # اضافه کردن نقش به پاسخ
                        'phone_number': token['phone_number'],  # اضافه کردن شماره موبایل به پاسخ
                        'id': token['id'],  # اضافه کردن id به پاسخ
                    },
                    'is_new': is_new,
                    'is_verified': user.is_verified
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response({
                    'message': 'Invalid OTP',
                    'status': status.HTTP_400_BAD_REQUEST,
                })
        except User.DoesNotExist:
            return Response({
                'message': 'User not found',
                'status': status.HTTP_404_NOT_FOUND,
            })

class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        try:
            # Invalidate refresh token by blacklisting it
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response({
                    'message': 'Logout successfully',
                    'status': status.HTTP_200_OK,
                })
            else:
                return Response({
                    'message': 'Refresh token is required',
                    'status': status.HTTP_400_BAD_REQUEST,
                })
        except Exception as e:
            return Response({
                'message': str(e),
                'status': status.HTTP_400_BAD_REQUEST,
            })


# update user database

class UserUpdateView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(id=self.request.user.id)

    def update(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            'message': _('Profile updated successfully'),
            'status': status.HTTP_200_OK,
            'data': serializer.data,
        })

    def perform_update(self, serializer):
        serializer.save()

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class CreateClientProfileApiView(generics.RetrieveUpdateAPIView):
    serializer_class = CreateClientProfileSerializer
    permission_classes = [IsAuthenticated]  # اطمینان از احراز هویت کاربر

    def get_object(self):
        # فرض می‌کنیم پروفایل با توجه به یوزر احراز هویت شده پیدا می‌شود
        return self.request.user.clientprofile

    def perform_create(self, serializer):
        # پروفایل را ذخیره می‌کند
        profile = serializer.save(user=self.request.user)
        return Response({"message": "Profile created successfully."}, status=status.HTTP_201_CREATED)

class CreateClientProfileApiView(generics.CreateAPIView):
    serializer_class = CreateClientProfileSerializer
    permission_classes = [IsAuthenticated]  # اطمینان از احراز هویت کاربر

    def perform_create(self, serializer):
        # پروفایل را ذخیره می‌کند
        profile = serializer.save()
        return Response({"message": "Profile created successfully."}, status=status.HTTP_201_CREATED)

class CreateNurseProfileApiView(generics.CreateAPIView):
    serializer_class = CreateNurseProfileSerializer
    permission_classes = [IsAuthenticated]  # اطمینان از احراز هویت کاربر

    def perform_create(self, serializer):
        # پروفایل را ذخیره می‌کند
        profile = serializer.save()
        return Response({"message": "Nurse profile created successfully."}, status=status.HTTP_201_CREATED)
