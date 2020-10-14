import uuid
from django.db import models

from .user import User


class CustomReportService(models.Model):
    """
    Represent a 3rd party service whose reports do not depend on data acquired through Sensehel
    """
    name = models.CharField(max_length=32)
    img_logo_url = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.name


class CustomReportSubscription(models.Model):
    """
    User subscribes to a service
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custom_subscriptions')
    service = models.ForeignKey(CustomReportService, on_delete=models.CASCADE, related_name='subscriptions')
    report_url = models.URLField(default='', help_text='URL to the main page presenting a subscription')
    preview_url = models.URLField(
        default='',
        help_text='URL that renders a compact subscription report for inclusion as iframe in user home view')

    def __str__(self):
        return f'User {self.user} subscription for {self.service}'
