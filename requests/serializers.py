"""
Serialing the data for request app.
"""
from rest_framework import serializers
from models import Request
from accounts.models.profiles import NurseProfile


class RequestSerializer(serializers.ModelSerializer):
    """Serializing the requests data."""
    
    class Meta:
        model = Request
        fields = '__all__'
    extra_kwargs = {
        'client': {'read_only': True},
        'created_date':{'read_only': True}, 
    }



class NurseListSerializer(serializers.Serializer):
    """Serilizing nurse profile objects."""
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    rate = serializers.FloatField()




