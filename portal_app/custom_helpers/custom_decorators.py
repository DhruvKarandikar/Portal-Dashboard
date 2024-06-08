import logging
from functools import wraps
from typing import Callable, Any
from portal_app.custom_helpers.serializer_helpers import CustomExceptionHandler
from portal_app.custom_helpers.consts_status_code import generic_error_1
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view as og_api_view
from rest_framework.serializers import Serializer

logger = logging.getLogger('django')


def custom_api_view(
        request_serializer,
        http_method_names=None,
        responses=None,
        operation_id=None,
):
    """
    A custom decorator for defining API views with request validation and Swagger documentation.

    Args:
        request_serializer (Serializer | Callable): The serializer class for the request data validation.
        http_method_names (list[str]): List of HTTP methods supported by the view (e.g., ["GET", "POST"]). Defaults to ["POST"] if not provided.
        responses (dict[str, Serializer | Callable]): List of responses
        operation_id (str): operation_id to be added in swagger schema
    Returns:
        None
    """

    http_method_names = ['post'] if (http_method_names is None) else http_method_names

    def decorator(function: Callable):
        kwargs = {
            "method": http_method_names[0],
            "request_body": request_serializer,
            "responses": responses,
            "operation_id": operation_id,
        }

        @swagger_auto_schema(**kwargs)
        @og_api_view(http_method_names=http_method_names)
        @validate_request(validation_serializer=request_serializer)
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            logger.info(f"Request from url:{request.build_absolute_uri()} --> view function {function.__name__}")
            response_obj = function(request, *args, **kwargs)
            return response_obj

        return wrapper

    return decorator


def validate_request(validation_serializer):
    """
    Warning:
        - DO NOT USE THIS DECORATOR WITH CLASS METHODS

    NOTE:
        - The Request arg must be named request or the used arg name should be passed in the request_param.
        - The Serialised data will be added to request itself.

    Args:
        validation_serializer (Serializer | Callable): Serializer for the given request.
    Raises:
        CustomExceptionHandler
            - generic_error_1
    Returns:
        None
    """

    def decorator(function: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(function)
        def wrapper(request, *args: Any, **kwargs: Any) -> Any:
            request.validation_serializer = validation_serializer(data=request.data)
            if not request.validation_serializer.is_valid():
                logger.debug(f'sbhsbgebseuboseubgo {request}')
                logger.exception(f'The Request is improper. Exact details:: {request.validation_serializer.errors}')
                raise CustomExceptionHandler(generic_error_1)

            return function(request, *args, **kwargs)

        return wrapper

    return decorator

