"""
Serialing the data for request app.
"""
from rest_framework import serializers
from .models import Request
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



class RequstPostSerializer(serializers.Serializer):
    '''Serialize data to post a request.'''
    nurse = serializers.IntegerField()




class NurseListSerializer(serializers.Serializer):
    """Serilizing nurse profile objects."""
    id = serializers.IntegerField()
    user__first_name = serializers.CharField()
    user__last_name = serializers.CharField()
    average_rate = serializers.FloatField()
    salary_per_hour = serializers.FloatField()



class NurseSeriliazr(serializers.ModelSerializer):
    """Serializer nurse salary prfile"""
    
    class Meta:
        model = NurseProfile
        fields = '__all__'


