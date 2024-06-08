from portal_app.custom_helpers.consts_status_code import *
from portal_app.custom_helpers.serializer_helpers import CustomExceptionHandler, create_update_model_serializer
from portal_app.models import *
from portal_app.serializers.portal_app_serializer import HeadPortalDashboardSerializer


def get_dashboard_service(request_data):

    dashboard_objs = []
    portal_model_query_obj = PortalDetail.objects.all()

    end_year = request_data.get("end_year", None)
    topic = request_data.get("topic", None)
    sector = request_data.get("sector", None)
    region = request_data.get("region", None)
    country = request_data.get("country", None)
    pestle = request_data.get("pestle", None)
    source = request_data.get("source", None)

    if request_data is None:
        portal_model_query_obj = portal_model_query_obj
    else:
        if end_year:
            portal_model_query_obj = portal_model_query_obj.filter(end_year=end_year)
        if topic:
            portal_model_query_obj = portal_model_query_obj.filter(topic__icontains=topic)
        if sector:
            portal_model_query_obj = portal_model_query_obj.filter(sector__icontains=sector)
        if region:
            portal_model_query_obj = portal_model_query_obj.filter(region__icontains=region)
        if country:
            portal_model_query_obj = portal_model_query_obj.filter(country__icontains=country)
        if pestle:
            portal_model_query_obj = portal_model_query_obj.filter(region__icontains=region)
        if source:
            portal_model_query_obj = portal_model_query_obj.filter(pestle__icontains=pestle)

    if portal_model_query_obj:
        dashboard_objs = HeadPortalDashboardSerializer(portal_model_query_obj, many=True)
        return get_response(success, data=dashboard_objs.data)
    else:
        return get_response(success, data=[])


def crud_portal_service(request_data):

    final_list = []

    for portal_obj in request_data:
        instance_portal_obj = create_update_model_serializer(HeadPortalDashboardSerializer,portal_obj,partial=True)
        final_list.append(instance_portal_obj)

    return get_response(success, data=HeadPortalDashboardSerializer(final_list, many=True).data)




