from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()
# Create your serializers here.
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "phone_number",]
        extra_kwargs = {
            "id": {"read_only": True},
            "phone_number": {"required": True},
        }
def create(self, validated_data):
        user = User.objects.create(**validated_data)
        return user


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