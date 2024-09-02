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


class RequestSerializerExtra(serializers.Serializer):
    '''Serializing requests with extra informations.'''
    id = serializers.IntegerField()
    client = serializers.IntegerField()
    client__user__first_name = serializers.CharField()
    client__user__last_name = serializers.CharField()
    nurse = serializers.IntegerField()
    nurse__user__first_name = serializers.CharField()
    nurse__user__last_name = serializers.CharField()
    created_date = serializers.DateTimeField()
    request_for_date = serializers.CharField()
    request_start = serializers.CharField()
    duration_hours = serializers.FloatField()
    request_end = serializers.CharField()
    address = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    for_others = serializers.BooleanField()
    status = serializers.CharField()
    rate = serializers.BooleanField()
    category = serializers.CharField()
    payment = serializers.FloatField()
    other_information = serializers.JSONField()


        

