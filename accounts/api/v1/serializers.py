from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()
# Create your serializers here.


class VerifyPhoneOTPModelSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6)

    class Meta:
        model = User
        fields = ['phone_number', 'otp']

    def validate(self, data):
        phone_number = data.get('phone_number')
        otp = data.get('otp')
        
        try:
            # Retrieve the user based on phone number
            user = User.objects.get(phone_number__iexact=phone_number)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this phone number does not exist.")

        # Check if the OTP matches
        if user.otp != otp:
            raise serializers.ValidationError("The OTP does not match.")

        # Return the validated data
        return data

class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'birthday', 'national_id', 'avatar', 'national_card_image', 'password', 'password_confirm']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'password_confirm': {'write_only': True, 'required': False},
        }

    def validate(self, data):
        password = data.get('password')
        password_confirm = data.pop('password_confirm', None)

        if password and password_confirm:
            if password != password_confirm:
                raise serializers.ValidationError("Passwords do not match.")

        return data

    def update(self, instance, validated_data):
        # بررسی و به‌روزرسانی پسورد در صورت وجود
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        
        # بررسی عکس کارت ملی و تنظیم is_verified
        if 'national_card_image' in validated_data and validated_data['national_card_image']:
            instance.is_verified = True
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        return super().update(instance, validated_data)