import uuid
from django.db import models

from .sensor_models import SensorAttribute


class Service(models.Model):
    """
    Represent a 3rd party service provider
    """
    name = models.CharField(max_length=32)
    price = models.CharField(max_length=8)
    benefit_short = models.CharField(max_length=20)
    benefit_long = models.CharField(max_length=255)
    description = models.TextField(max_length=512)

    requires = models.ManyToManyField(
        SensorAttribute, related_name='services',
        help_text='At least one of these attributes must be included in any subscription to this service.')

    eula_url = models.CharField(max_length=255)
    img_logo_url = models.CharField(max_length=255, null=True)
    img_service_url = models.CharField(max_length=255, null=True)

    subscribe_url = models.URLField(default='', help_text='URL to which new subscriptions should be POSTed')
    unsubscribe_url = models.URLField(default='', help_text='URL to which unsubscribe requests should be POSTed')
    data_url = models.URLField(default='', help_text='URL to which sensor data should be POSTed')
    report_url = models.URLField(default='', help_text='URL to the main page presenting a subscription')
    preview_url = models.URLField(
        default='',
        help_text='URL that renders a compact subscription report for inclusion as iframe in user home view')

    auth_token = models.UUIDField(
        default=uuid.uuid4,
        help_text='Token that SenseHel will include in all outgoing POST requests as authentication')

    def __str__(self):
        return self.name

    @classmethod
    def list_available_for_user(cls, user):
        return cls.objects.filter(requires__sensors__apartmentsensor__apartment__user=user).distinct()