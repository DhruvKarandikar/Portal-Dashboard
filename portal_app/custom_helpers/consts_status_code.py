DEFAULT_ROLE = "local_system"
STATUS_ACTIVE = 1
CREATION_BY = "system"
HTTP_REQUEST_ID = 'local_id'

DATE_FORMAT = "date_format"
TIME_FORMAT = "time_format"

DATE_YYYY_MM_DD = "%Y-%m-%d"
DATE_YYYY_MM_DD_HH_MM_SS = "%Y-%m-%d %H:%M:%S"
DATE_YYYY_MM = "%Y-%m"
TIME_HH_MM_SS = "%H:%M:%S"
DATE_MM_DD_YYYY = "%-m/%d/%Y"
DATE_DD_MM_YYYY = "%d-%m-%Y"
DATE_YYYY = "%Y"


STATUS_CODE = 'status_code'
SUCCESS_CODE = 10000
MESSAGE = 'message'

COMMON_CHECK_FORMAT_TYPE = {
        DATE_FORMAT: 10,
        TIME_FORMAT: 11
}

success = {STATUS_CODE: SUCCESS_CODE, MESSAGE: "Success"}

def invalid_log_model(table_name):
    return {
        STATUS_CODE: 2100001,
        MESSAGE: f'Invalid log model initialized for model {table_name}',
    }

generic_error_1 = {STATUS_CODE: int(f"2110000"), MESSAGE: "Invalid request details"}
generic_error_2 = {STATUS_CODE: int(f"2110001"), MESSAGE: "Please try again after sometime"}

def obj_not_found(id,model):
    return {'status_code': 2110003, 'message': f'id = {id} not exist in {model}'}

def error_in_serializer(serializer_name):
    return {'status_code': 2110004, 'message': f'error in serializer {serializer_name} '}

def get_response(status_attribute, data=None):
    if data is None:
        return {'status': status_attribute['status_code'], 'message': status_attribute['message']}
    else:
        return {'status': status_attribute['status_code'], 'message': status_attribute['message'], 'data': data}

def log_info_message(request, message = "Info"):
    return (f"{message} --> {request.body}")

