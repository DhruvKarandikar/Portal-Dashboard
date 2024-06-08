from django.db import models
from portal_app.custom_helpers.model_helpers import AddCommonField


class CommonPortalDetail(AddCommonField):

    id = models.BigAutoField(primary_key=True)
    start_year = models.IntegerField(null=True)
    end_year = models.IntegerField(null=True)
    intensity = models.IntegerField(null=True)
    sector = models.TextField(null=True)
    topic = models.TextField(null=True)
    insight = models.TextField(null= True)
    url = models.TextField(null= True)
    region = models.TextField(null= True)
    impact = models.TextField(null= True)
    added = models.TextField(null= True)
    published = models.TextField(null= True)
    country = models.TextField(null= True)
    relevance = models.IntegerField(null= True)
    pestle = models.TextField(null= True)
    source = models.TextField(null= True)
    title = models.TextField(null= True)
    likelihood = models.IntegerField(null= True)

    class Meta:
        abstract = True


class PortalDetail(CommonPortalDetail):

    class Meta:
        db_table = "portal_detail"

