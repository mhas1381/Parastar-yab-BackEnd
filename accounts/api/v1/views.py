from rest_framework.response import Response
from rest_framework import viewsets, status,permissions
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import VerifyPhoneOTPModelSerializer,UserUpdateSerializer
from .utils import otp_generator
User = get_user_model()


def send_otp(phone_number):
    if phone_number:
        key = otp_generator()
        phone_number = str(phone_number)
        otp_key = str(key)
        print(otp_key)
        return otp_key
    return False

class ValidatePhoneSendOTP(APIView):
    def get(self, request, phone_number, role=None, *args, **kwargs):
        try:
            # اگر role ارسال نشده باشد، به صورت پیش‌فرض CLIENT قرار می‌گیرد
            role = role if role else User.Role.CLIENT
            
            if phone_number:
                phone_number = str(phone_number).strip()
                
                # اگر کاربری با این شماره موجود نباشد، ایجادش کنید
                user, created = User.objects.get_or_create(phone_number=phone_number)

                # اگر کاربر جدید است، نقش را تنظیم کنید
                if created:
                    user.role = role
                    user.save()
                
                # ارسال OTP و ذخیره زمان ارسال
                new_otp = send_otp(phone_number)
                user.otp = new_otp
                user.otp_created_at = timezone.now()
                user.save()

                return Response({
                    'message': 'OTP sent successfully',
                    'status': status.HTTP_200_OK,
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

            
            if user.otp_created_at and timezone.now() > user.otp_created_at + timedelta(minutes=2):
                return Response({
                    'message': 'OTP has expired',
                    'status': status.HTTP_400_BAD_REQUEST,
                })

            if user.otp == otp:
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)

                return Response({
                    'status': True,
                    'details': 'Login Successfully',
                    'token': {
                        'refresh': refresh_token,
                        'access': access_token,
                    },
                    'response': {
                        'id': user.id,
                        'phone_number': user.phone_number,
                        'role':user.role
                    }
                }, status=status.HTTP_200_OK)
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