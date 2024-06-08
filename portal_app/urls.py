from django.urls import path
from portal_app.views import *

urlpatterns = [

    # paths for vendor

    path('portal_app/get_portal_details', get_portal_dashboard, name='portal_get'),
    path('portal/portal_details', portal_dashboard_create_update, name='portal_crud'),
]
