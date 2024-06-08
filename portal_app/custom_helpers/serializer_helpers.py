from django.db.models.query import QuerySet, Q
from django.db import models
from django.utils import timezone
from portal_app.custom_helpers.consts_status_code import *
from rest_framework.serializers import ModelSerializer
import datetime
from functools import wraps
from django.core.exceptions import FieldError
from django.db.models.fields.related import ForeignKey, OneToOneField, ManyToManyField, ManyToOneRel, ManyToManyRel, OneToOneRel
import copy
from portal_app.custom_helpers.model_helpers import *
from typing import Any, Type
import logging

logger = logging.getLogger('django')


class CustomUpdateManager(QuerySet):
    logModel_config = {}

    @staticmethod
    def set_logModel(logModel, model):
        # map model with its respective log model
        CustomUpdateManager.logModel_config[model] = logModel   

    def update(self, *args, **kwargs):

        logModel_name = CustomUpdateManager.logModel_config.get(self.model.__name__)
        logModel = None
        from django.apps import apps
        for app in apps.get_app_configs():      
            # iterate over all models in an app configuration and get its log model
            for model in app.get_models():          
                if model.__name__ == logModel_name:
                    logModel = model
                    break

        if logModel:
            instances = [instance.id for instance in self]
            super().update(*args, **kwargs)        # updation
            instances = self.model.objects.filter(id__in=instances)

            for instance in instances:
                # add its log by storing the object
                add_log_model(logModel, instance, logModel.__name__)       
        else:
            # if log model not found
            raise CustomExceptionHandler(invalid_log_model(self.model.__name__))

class ActiveQuerySetManager(CustomUpdateManager):
    @staticmethod
    def _extract_fields_from_Q_object(q: Q):
        """
        Extract fields from the keyword arguments provided during the initialization of Q objects.
        """
        for child in q.children:
            # contains keyword argument as tuples or Q object
            # Inside tuple the first element will be key of keyword argument which will be returned
            if isinstance(child, tuple):
                child = child[0]
                yield child
            if isinstance(q, Q):
                ActiveQuerySetManager._extract_fields_from_Q_object(child)

    @staticmethod
    def get_status_active_kwargs_for_kwarg(model:Type[models.Model],field,exclude,*args,**kwargs) -> dict:
        """
        This function returns a dictionary of keyword arguments which contains all the required status fields set to active .
        """
        reserved_nonfield_keywords = ["exact","iexact","contains","icontains","in","gt","gte","lt","lte","startswith","istartswith","endswith","iendswith","range","date","year","iso_year","month","day","week","week_day","iso_week_day","quarter","time","hour","minute","second","isnull","regex","iregex"]
        # get all related fields from current model
        related_fields = {field.name: field for field in model._meta.get_fields() if isinstance(field, (ForeignKey, ManyToManyField, OneToOneField, ManyToOneRel, ManyToManyRel, OneToOneRel))}

        if "__" in field:
            first, *rest = field.split("__")
            if first in related_fields and rest[0] not in reserved_nonfield_keywords and f"{first}__status" not in kwargs.keys():
                # Makes sure that status is not already provided in keyword arguments
                status_active_kwargs = {f"{first}__status": 1} if not exclude else {f"{first}__status": 0}
                recursive_status_active_kwargs = ActiveQuerySetManager.get_status_active_kwargs_for_kwarg(related_fields.get(first).related_model, "__".join(rest),exclude,**kwargs)
                relative_recursive_status_active_kwargs = {
                    f"{first}__{key}": value for key, value in recursive_status_active_kwargs.items()
                }
                return {
                    **status_active_kwargs,
                    **relative_recursive_status_active_kwargs
                }
                
        return {}
    
    def _inject_status_active_in_kwargs(function):
        """
        This decorator replaces the kwargs with new set of kwargs which contains the status active kwargs
        """
        @wraps(function)
        def wrapper(instance, *args, **kwargs):
            Qs = [arg for arg in args if isinstance(arg, Q)]
            fields_extracted_from_Q = []

            for q in Qs:
                # If arguments has Q model objects
                fields_extracted_from_Q += list(ActiveQuerySetManager._extract_fields_from_Q_object(q))

            new_kwargs = copy.deepcopy(kwargs)
            exclude = False
            if function.__name__=="exclude":
                exclude = True

            status_active_kwargs = {"status": 1} if not exclude else {"status": 0}

            if 'status' in new_kwargs and new_kwargs['status']==0:
                # If user provides the status of object as INACTIVE [ALLOWS OVERRIDING]
                status_active_kwargs['status']=0
            for kwarg in [*kwargs.keys(), *fields_extracted_from_Q]:
                status_active_kwargs = {
                    **status_active_kwargs,
                    **ActiveQuerySetManager.get_status_active_kwargs_for_kwarg(instance.model,kwarg,exclude,**kwargs)
                }
            try:
                new_kwargs = {
                    **new_kwargs,
                    **status_active_kwargs
                }
                return function(instance, *args, **new_kwargs)
            except FieldError as field_error:
                return function(instance, *args, **kwargs)
        return wrapper
    
    @_inject_status_active_in_kwargs
    def filter(self, *args: Any, **kwargs: Any):
        """
        Custom filter(): which by default contains statuses as ACTIVE set.
        """
        return super().filter(*args, **kwargs)
    
    def prefetch_related(self, *lookups, **filter_kwargs):
        """
        Custom prefetch_related(): which by default has query as status ACTIVE set.
        """
        filtered_qs = self.filter(**filter_kwargs)
        # call prefetch_related on the filtered QuerySet
        return super(filtered_qs.__class__, filtered_qs).prefetch_related(*lookups)

    @_inject_status_active_in_kwargs
    def get(self, *args: Any, **kwargs: Any):
        """
        Custom get(): status is set to ACTIVE in the query by default.
        """
        return super().get(*args, **kwargs)

    @_inject_status_active_in_kwargs
    def get_or_create(self, defaults=None, **kwargs):
        """
        Custom get_or_create(): status is set to ACTIVE in the query by default.
        """
        return super().get_or_create(defaults,**kwargs)
    
    @_inject_status_active_in_kwargs
    def update_or_create(self, defaults=None, **kwargs):
        """
        Custom update_or_create(): status is set to ACTIVE in the query by default.
        """
        return super().update_or_create(defaults, **kwargs)
    
    def first(self):
        """Custom first(): First object in the list with status ACTIVE"""
        queryset_value=self
        if not self.ordered:
            queryset_value = self.order_by('id','-status')
        for obj in queryset_value:
            return obj
    
    def last(self):
        """Custom last(): Last object in the list with status ACTIVE"""
        queryset_value=self
        if not self.ordered:
            queryset_value = self.order_by('id','-status')
        last_object=None
        for obj in queryset_value:
            last_object = obj
        return last_object


def dict_get_key_from_value(dict_obj, dict_val):
    try:
        if dict_val is not None:
            key_list = list(dict_obj.keys())
            val_list = list(dict_obj.values())
            try:
                position = val_list.index(int(dict_val))
            except:
                position = val_list.index(dict_val)
            return key_list[position]
        else: 
            return None 
    except:
        return None

def number_to_decimal(number_val):
    if number_val is not None:
        number_val = int(number_val) / 100
    return number_val

def string_to_integer(string_val):
    if string_val is not None:
        string_val = int(string_val)
    return string_val
    
def help_text_for_dict(dict_value):
    """
    Args:
        dict_value (_type_): Dict type

    Returns:
        _type_: String Format help text
    """
    return f'Enter value from this list - {list(dict_value.keys())}'


def get_datetime_to_str(datetime_obj, format, idx=0, format_type=COMMON_CHECK_FORMAT_TYPE[DATE_FORMAT]):
    from datetime import datetime
    
    if datetime_obj:
        if 'T' in datetime_obj:
            date = datetime_obj.split("T")[idx] 
        else:
            date = datetime_obj.split(" ")[idx]
        
        if COMMON_CHECK_FORMAT_TYPE[TIME_FORMAT] == format_type:
            date = datetime.strptime(date, TIME_HH_MM_SS)
        else:
            date = datetime.strptime(date, DATE_YYYY_MM_DD)
        if date:
            return datetime.strftime(date, format)
    return None


def common_checking_and_passing_value_from_list_dict(value, list_dict, error_label):
    """
    merged two functions common_dict_checking_and_passing_value, common_list_checking
    """
    if value == "":
        return None

    if value:
        if type(list_dict) == list:
            if value not in list_dict:
                raise CustomExceptionHandler(error_label)
            return value
        else:
            if type(value) == list:
                list_value = []
                for single_value in value:
                    if single_value not in list_dict.keys():
                        raise CustomExceptionHandler(error_label)
                    list_value.append(list_dict[single_value])
                return list_value
            
            if value not in list_dict.keys():
                raise CustomExceptionHandler(error_label)
                    
            return list_dict[value]
    return value


def comman_create_update_services(self, validated_data, instance = None):

    if not instance:
        instance = self.Meta.model.objects.create(**validated_data)

    else:
        updated_keys = []
        for key, value in validated_data.items():
            if value != None and key != 'id':
                updated_keys.append(key)
                setattr(instance, key, value)
        instance.save(update_fields = updated_keys)

    return instance



class CustomExceptionHandler(Exception):
    def __init__(self, message=''):
        # Call the base class constructor with the parameters it needs
        super(CustomExceptionHandler, self).__init__(message)





def get_model_data(modelName, q_parameter, error_code_1, error_code_2, no_obj_flag=False, multiple_obj_flag=False):
    try:
        return modelName.objects.get(q_parameter)
    except modelName.MultipleObjectsReturned as e:
        if multiple_obj_flag is True:
            return modelName.objects.filter(q_parameter)
        raise CustomExceptionHandler(error_code_1)
    except modelName.DoesNotExist as e:
        if no_obj_flag is True:
            return None
        raise CustomExceptionHandler(error_code_2)

def create_update_model_serializer(model_serializer: ModelSerializer, data: dict, additional_data: dict = {}, partial=False):

    """
    Mainly it performs  create and update   functions 
    This function takes a model serializer, data, additional data, and a partial flag as input parameters.
    It validates the data using the provided model serializer and returns the instance if the data is valid.
    Returns:
    - instance: The instance of the model if the data is valid.

    Raises:
    - CustomExceptionHandler: If there is an error in the serializer.

"""
    id = data.get('id')
    model = model_serializer.Meta.model
    if id:
        instance = get_model_data(model, Q(id=id), None, obj_not_found(id,model.__name__)) 
        serializer = model_serializer(instance, data=data, partial=True, context=additional_data)
    else:
        serializer = model_serializer(data=data, partial=partial, context=additional_data)
        
    if not serializer.is_valid():
        logger.error(f"error in serilizer is {serializer.errors}")
        raise CustomExceptionHandler(error_in_serializer(model_serializer))
    serializer.validated_data.update(additional_data)
    instance=serializer.save()
    return instance


