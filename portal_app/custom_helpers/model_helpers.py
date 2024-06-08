from portal_app.custom_helpers.consts_status_code import *
from portal_app.custom_helpers.serializer_helpers import CustomUpdateManager, CustomExceptionHandler
from django.db import models
import datetime
import threading
request_local = threading.local()


def get_request():
    return getattr(request_local, 'request', None)


def add_log_model(logModel, modelInstance, modelName, creation=False, status_change=False):
    """_summary_
    Args:
        logModel (_type_): Log Model that want to create/update 
        modelInstance (_type_): Model from which the data will be added
        modelName (_type_): Model Name use in error showing
    """
    try:
        logModel = logModel()
        logModel.__dict__ = modelInstance.__dict__.copy()
        logModel.id = None
        logModel.log = modelInstance
        request = get_request()
        logModel.creation_by = request.user_id if request else CREATION_BY
        logModel.creation_date = datetime.datetime.now()
        logModel.save()
        return logModel
    except Exception as e:
        raise CustomExceptionHandler(f'{modelName} Log')


class AddCommonField(models.Model):
    objects = CustomUpdateManager.as_manager()

    status = models.PositiveSmallIntegerField(null=False, default=STATUS_ACTIVE)
    creation_date = models.DateTimeField(null=False, auto_now_add=True)
    creation_by = models.TextField(null=False)
    updation_date = models.DateTimeField(null=True, auto_now=True)
    updation_by = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # Set the ‘updated_by’ field to the specified username or email
        update_field = kwargs.get('update_fields')
        if update_field:
            if "id" in update_field:
                update_field.remove('id')
            update_field.extend(["creation_date","creation_by",'updation_by',"updation_date"])
            
        if request := get_request():
            if not self.pk:
                self.creation_by = request.user_id
        else:
            self.creation_by = "Not API request"
            self.updation_by = "Not API request"
        super().save(*args, **kwargs)
        if not self.__dict__.get('log_id') and hasattr(self,'logs'):
            self.log_object = add_log_model(self.logs.model, self, self.__class__.__name__)

