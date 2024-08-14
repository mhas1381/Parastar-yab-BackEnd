from rest_framework.response import Response
from rest_framework import viewsets, status,permissions
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer,VerifyPhoneOTPModelSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import otp_generator
User = get_user_model()

class RegisterView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        headers = self.get_success_headers(serializer.data)

        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        return Response({
            'response': serializer.data,
            'success': True,
            'message': 'User created successfully',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'status': status.HTTP_201_CREATED,
        }, status=status.HTTP_201_CREATED, headers=headers)

def send_otp(phone_number):
    if phone_number:
        key = otp_generator()
        phone_number = str(phone_number)
        otp_key = str(key)
        print(otp_key)
        return otp_key
    return False
class ValidatePhoneSendOTP(APIView):
    def get(self, request, phone_number, *args, **kwargs):
        try:
            if phone_number:
                phone_number = str(phone_number).strip()
                user = User.objects.filter(phone_number__iexact=phone_number)

                if user.exists():
                    data = user.first()
                    new_otp = send_otp(phone_number)
                    data.otp = new_otp
                    data.save()
                    return Response({
                        'message': 'OTP sent successfully',
                        'status': status.HTTP_200_OK,
                    })
                else:
                    return Response({
                        'message': 'User not found! Please register.',
                        'status': status.HTTP_404_NOT_FOUND,
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

        # Extract validated data
        phone_number = serializer.validated_data['phone_number']
        user = User.objects.get(phone_number__iexact=phone_number)

        # Generate JWT token
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
            }
        }, status=status.HTTP_200_OK)

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