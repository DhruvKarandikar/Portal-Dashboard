from rest_framework import serializers
from django.db.models import Q
from portal_app.models import *
from django.db.transaction import atomic
from portal_app.custom_helpers.serializer_helpers import string_to_integer, CustomExceptionHandler, comman_create_update_services
from portal_app.custom_helpers.consts_status_code import *
import logging
logger = logging.getLogger("django")

class HeadPortalDashboardSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(required=False)
    start_year = serializers.CharField(required=False, allow_blank=True)
    end_year = serializers.CharField(required=False, allow_blank=True)
    intensity = serializers.IntegerField(required=False)
    sector = serializers.CharField(required=False, allow_blank=True)
    topic = serializers.CharField(required=False, allow_blank=True)
    insight = serializers.CharField(required=False, allow_blank=True)
    url = serializers.CharField(required=False, allow_blank=True)
    region = serializers.CharField(required=False, allow_blank=True)
    impact = serializers.CharField(required=False, allow_blank=True)
    added = serializers.CharField(required=False, allow_blank=True)
    published = serializers.CharField(required=False, allow_blank=True)
    country = serializers.CharField(required=False, allow_blank=True)
    relevance = serializers.IntegerField(required=False)
    pestle = serializers.CharField(required=False, allow_blank=True)
    source = serializers.CharField(required=False, allow_blank=True)
    title = serializers.CharField(required=False, allow_blank=True)
    likelihood = serializers.IntegerField(required=False)

    class Meta:
        model = PortalDetail
        exclude = ("status", "creation_date", "creation_by", "updation_date", "updation_by",)
    
    def validate(self, data):
        data = super().validate(data)
        return {key: (value if value != "" else None) for key, value in data.items()}

    def validate_end_year(self, value):
        if value in [None, ""]:
            value = 0
        else:
            value = string_to_integer(value)
        return value
    
    def validate_start_year(self, value):
        if value in [None, ""]:
            value = 0
        else:
            value = string_to_integer(value)
        return value
    
    def to_representation(self, data):
        data = super().to_representation(data)
        if data.get("start_year") is None:
            data['start_year'] = ""
        else:
            data['start_year'] = str(data["start_year"]) 
        
        if data.get("end_year") is None:
            data['end_year'] = ""
        else:
            data['end_year'] = str(data["end_year"]) 

        return data

    @atomic
    def create(self, validated_data):
        return comman_create_update_services(self, validated_data)

    @atomic
    def update(self, instance, validated_data):
        return comman_create_update_services(self, validated_data, instance)


# create update serializer
class PortalDetailCreateUpdateRequestSerializer(HeadPortalDashboardSerializer):

    class Meta:
            model = PortalDetail
            fields = ("id", "start_year", "end_year", "intensity", 
                    "sector", "topic", "insight", "url", "region", 
                    "impact", "added", "published", "country","relevance", 
                    "pestle", "source", "title", "likelihood",)



class PortalDetailCrudReponseSerializer(HeadPortalDashboardSerializer):
    status = serializers.IntegerField(help_text = "Status Code", required = False)
    message = serializers.CharField(help_text = "Status Message", required = False)
    data = HeadPortalDashboardSerializer(required=False, many=True)

    class Meta:
            model = PortalDetail
            fields = ("status", "message", "data",)



class GetPortalDetailRequestSerializer(serializers.ModelSerializer):

    end_year = serializers.CharField(required=False, allow_blank=True)
    topic = serializers.CharField(required=False, allow_blank=True)
    sector = serializers.CharField(required=False, allow_blank=True)
    region = serializers.CharField(required=False, allow_blank=True)
    country = serializers.CharField(required=False, allow_blank=True)
    pestle = serializers.CharField(required=False, allow_blank=True)
    source = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = PortalDetail
        fields = ("end_year", "sector", "topic", "region", 
                "country", "pestle", "source",)

    def validate_end_year(self, value):
        if value in [None, ""]:
            value = 0
        else:
            value = string_to_integer(value)
        return value


    def to_representation(self, data):
        data = super().to_representation(data)
        
        if data.get("start_year") is None:
            data['start_year'] = ""
        else:
            data['start_year'] = str(data["start_year"].year) 
        
        if data.get("end_year") is None:
            data['end_year'] = ""
        else:
            data['end_year'] = str(data["start_year"].year) 

        return data
    
    def validate(self, data):
        data = super().validate(data)
        return {key: (value if value != "" else None) for key, value in data.items()}


class GetPortalDetailResponseSerializer(HeadPortalDashboardSerializer):
    status = serializers.IntegerField(help_text = "Status Code", required = False)
    message = serializers.CharField(help_text = "Status Message", required = False)
    data = HeadPortalDashboardSerializer(required=False, many=True)

    class Meta:
            model = PortalDetail
            fields = ("status", "message", "data",)

