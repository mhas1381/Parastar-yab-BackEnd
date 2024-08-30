from rest_framework.response import Response
from rest_framework import viewsets, status,permissions
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
# from kavenegar import *
from .serializers import *
from .utils import otp_generator
from accounts.models import *
User = get_user_model()


def send_otp(phone_number):
    if phone_number:
        pass
        try:
            key = otp_generator()
            phone_number = str(phone_number)
            otp_key = str(key)
            print(f"Generated OTP: {otp_key}")  # For debugging purposes

    #         # Send OTP using Kavenegar
    #         api = KavenegarAPI(settings.KAVENEGAR_API_KEY)  # Replace with your Kavenegar API key
    #         params = {
    #             'sender': settings.KAVENEGAR_SENDER,
    #             'receptor': phone_number,
    #             'message': f'Your OTP is: {otp_key}',
    #         }
    #         response = api.sms_send(params)
    #         print(f"SMS Response: {response}")  # For debugging purposes

            return otp_key
    #     except APIException as e:
    #         print(f"Kavenegar API Exception: {e}")
    #         return False
    #     except HTTPException as e:
    #         print(f"Kavenegar HTTP Exception: {e}")
    #         return False
    #     except Exception as e:
    #         print(f"Error sending OTP: {e}")
    #         return False
    # return False
        except:
            print('there is otp problem')


class ValidatePhoneSendOTP(APIView):
    def get(self, request, phone_number, role=None, *args, **kwargs):
        try:
            # If role is not provided, set it to CLIENT by default
            role = role if role else User.Role.CLIENT
            
            if phone_number:
                phone_number = str(phone_number).strip()
                
                # Get or create the user based on the phone number
                user, created = User.objects.get_or_create(phone_number=phone_number)

                # If the user is newly created, set their role
                if created:
                    user.role = role
                    user.save()
                
                # Send OTP and store the time it was sent
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

            if user.otp_created_at and timezone.now() > user.otp_created_at + timedelta(minutes=2):
                return Response({
                    'message': 'OTP has expired',
                    'status': status.HTTP_400_BAD_REQUEST,
                })

            if user.otp == otp:
                # استفاده از توکن سفارشی
                token = CustomTokenObtainPairSerializer.get_token(user)

                return Response({
                    'status': True,
                    'details': 'Login Successfully',
                    'token': {
                        'refresh': str(token),
                        'access': str(token.access_token),
                        'role': token['role'],  # اضافه کردن نقش به پاسخ
                        'phone_number': token['phone_number'],  # اضافه کردن شماره موبایل به پاسخ
                        'id': token['id'],  # اضافه کردن id به پاسخ
                    },
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

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class ClientProfileViewSet(viewsets.ModelViewSet):
    queryset = ClientProfile.objects.all()
    serializer_class = ClientProfileSerializer

class NurseProfileViewSet(viewsets.ModelViewSet):
    queryset = NurseProfile.objects.all()
    serializer_class = NurseProfileSerializer
