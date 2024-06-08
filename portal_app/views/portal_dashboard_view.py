import json
import logging
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from portal_app.custom_helpers.consts_status_code import get_response, generic_error_2
from portal_app.custom_helpers.serializer_helpers import CustomExceptionHandler
from portal_app.serializers.portal_app_serializer import *
from portal_app.services.portal_app_dashboard_service import get_dashboard_service, crud_portal_service
from portal_app.custom_helpers.custom_decorators import custom_api_view

logger = logging.getLogger("django")

# Portal API
@csrf_exempt
@custom_api_view(
    request_serializer=GetPortalDetailRequestSerializer,
    responses={"200": GetPortalDetailResponseSerializer(many=True)},
    operation_id="Get Portal Information"
)
def get_portal_dashboard(request):
    response_obj = None

    try:
        logger.info(request, "request for vendor delete")
        response_obj = get_dashboard_service(request.validation_serializer.validated_data)

    except CustomExceptionHandler as e:
        logger.exception(f"Custom Exception in vendor delete url: {e}")
        response_obj = get_response(eval(str(e)))

    except Exception as e:
        logger.exception(f"Exception in vendor delete url {e}")
        response_obj = get_response(generic_error_2)

    logger.info("response in vendor delete --> %s", response_obj)
    return JsonResponse(response_obj, safe=False)



@csrf_exempt
@swagger_auto_schema(
    methods=['post'],
    request_body=PortalDetailCreateUpdateRequestSerializer(many=True),
    responses={"200": PortalDetailCrudReponseSerializer(many=True)},
    operation_id="Create Update Portal information"
)
@api_view(["POST"])
def portal_dashboard_create_update(request):
    response_obj = None

    try:
        logger.info(request, "request for get vendor details")
        response_obj = crud_portal_service(request.data)

    except CustomExceptionHandler as e:
        logger.exception(f"Custom Exception in get vendor details url: {e}")
        response_obj = get_response(eval(str(e)))

    except Exception as e:
        logger.exception(f"Exception in get vendor details url {e}")
        response_obj = get_response(generic_error_2)

    logger.info("response in get vendor details --> %s", response_obj)
    return JsonResponse(response_obj, safe=False)


