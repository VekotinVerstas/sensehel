import requests
import uuid
from django.core.mail import mail_admins
from django.db import models
from django.utils import timezone
from requests import HTTPError
from rest_framework import serializers

from .apartment_sensor_models import ApartmentSensorAttribute, ApartmentSensorValue
from .service import Service
from .user import User


class Subscription(models.Model):
    """
    User subscribes to a service
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='subscriptions')
    attributes = models.ManyToManyField(ApartmentSensorAttribute, related_name='subscriptions')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    registered = models.DateTimeField(null=True, editable=False)

    def __str__(self):
        return f'User {self.user} subscription for {self.service}'

    def _post(self, *args, **kwargs):
        # Defined here in order to be easily mockable for testing.
        return requests.post(*args, **kwargs)

    def create_in_service(self):
        """
        Register this subscription with the remote service.
        """
        serializer = CreateSubscriptionSerializer(self)
        response = self._post(self.service.subscribe_url, json=serializer.data)
        response.raise_for_status() # Raises exception if status code >=400
        self.registered = timezone.now()
        self.save()

    def delete_in_service(self):
        """
        Delete this subscription in the remote service.
        """
        data = {'uuid': str(self.uuid), 'auth_token': str(self.service.auth_token)}
        response = self._post(self.service.unsubscribe_url, json=data)
        response.raise_for_status()  # Raises exception if status code >=400

    def send_values(self, values):
        """
        Send the passed values to the external service.
        """
        data = SubscriptionDataSerializer(self, values=values).data
        response = self._post(self.service.data_url, json=data)
        response.raise_for_status()  # Raises exception if status code >=400

    def submit_history(self):
        """
        Send existing data values for the ApartmentSensorAttributes connected to this subscription to the
        external service. Intended to provide new subscriptions with any already collected data.
        """
        self.send_values(self.list_values())

    def list_values(self):
        return ApartmentSensorValue.objects.filter(apartment_sensor_attribute__subscriptions=self).distinct()

    @classmethod
    def handle_new_values(cls, new_values):
        """
        For every subscription related to any of the passed values, send the appropriate subset of values to the
        external service.
        """
        value_ids = [v.id for v in new_values]
        attr_ids = [v.apartment_sensor_attribute_id for v in new_values]
        for subscription in cls.objects.filter(attributes__in=attr_ids).distinct():
            try:
                subscription.send_values(subscription.list_values().filter(id__in=value_ids))
            except HTTPError as e:
                mail_admins(f'Sensehel service error: {subscription.service}', str(e), fail_silently=True)


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Base serializer used by the Subscription model when serializing for the remote service.
    """
    auth_token = serializers.CharField(source='service.auth_token')

    class Meta:
        model = Subscription
        fields = ('uuid', 'auth_token')


class ApartmentSensorAttributeSerializer(serializers.ModelSerializer):
    """
    Serializer used by the Subscription model when creating a new subscription in the remote service.
    """
    description = serializers.CharField(source='attribute.description')
    uri = serializers.CharField(source='attribute.uri')

    class Meta:
        model = ApartmentSensorAttribute
        fields = ('id', 'uri', 'description')


class CreateSubscriptionSerializer(SubscriptionSerializer):
    """
    Serializer used by the Subscription model when creating a new subscription in the remote service.
    """
    attributes = ApartmentSensorAttributeSerializer(many=True)

    class Meta(SubscriptionSerializer.Meta):
        fields = ('uuid', 'attributes', 'auth_token')


class ApartmentSensorValueSerializer(serializers.ModelSerializer):
    """
    Serializer used by the Subscription model when submitting values to the remote service.
    """
    attribute = serializers.IntegerField(source='apartment_sensor_attribute_id')
    timestamp = serializers.DateTimeField(source='updated_at')

    class Meta:
        model = ApartmentSensorValue
        fields = ('attribute', 'value', 'timestamp')


class SubscriptionDataSerializer(SubscriptionSerializer):
    """
    Serializer used by the Subscription model when submitting values to the remote service.
    """
    values = serializers.SerializerMethodField()

    class Meta(SubscriptionSerializer.Meta):
        fields = ('uuid', 'values', 'auth_token')

    def __init__(self, *args, values=[], **kwargs):
        super().__init__(*args, **kwargs)
        self._values = values

    def get_values(self, subscription):
        return ApartmentSensorValueSerializer(self._values, many=True).data
