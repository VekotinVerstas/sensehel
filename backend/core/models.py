import requests
import uuid
from django.contrib.auth.models import AbstractUser
from django.core.mail import mail_admins
from django.db import models
from django.utils import timezone
from requests import HTTPError
from rest_framework import serializers


class User(AbstractUser):
    """
    From AbstractUser relevant fields

    username
    first_name
    last_name
    email

    See baseclass for full details
    """

    phone = models.IntegerField(null=True)
    invite_code = models.CharField(max_length=64)

    # Ask non null field values during createsuperuser
    REQUIRED_FIELDS = AbstractUser.REQUIRED_FIELDS + ['phone']


class Apartment(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='apartments')
    street = models.CharField(max_length=64)
    city = models.CharField(max_length=32)
    postal_code = models.CharField(max_length=10)

    def __str__(self):
        return f'{self.user.first_name}, {self.user.last_name} - {self.street} ({self.postal_code})'


class ApartmentSensor(models.Model):
    """
    Represent a sensor in a apartment, taking measurements, physical installation

    `identifier`
        Used to identify physical product to be updated via APIs.
        Could be device serial number.
    """
    apartment = models.ForeignKey(
        Apartment, null=True, related_name='apartment_sensors', on_delete=models.SET_NULL)
    sensor = models.ForeignKey('Sensor', null=True, on_delete=models.SET_NULL)
    identifier = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f'Sensor {self.identifier} in apartment {self.apartment_id}'

    @classmethod
    def list_for_user(cls, user):
        return cls.objects.filter(apartment__user=user)


class ApartmentSensorAttribute(models.Model):
    """
    Represents one measured attribute of one particular ApartmentSensor; serves as the connecting element
    between ApartmentSensor, SensorAttribute and ApartmentSensorValues.
    """
    apartment_sensor = models.ForeignKey(ApartmentSensor, related_name='attributes', on_delete=models.CASCADE)
    attribute = models.ForeignKey(
        'SensorAttribute', on_delete=models.PROTECT, related_name='apartment_sensor_attributes')

    def __str__(self):
        return "Sensor {}: {}".format(self.apartment_sensor.identifier, self.attribute)

    def latest_value(self):
        return self.values.order_by('-updated_at').first()


class ApartmentSensorValue(models.Model):
    apartment_sensor_attribute = models.ForeignKey(
        ApartmentSensorAttribute, null=True, on_delete=models.CASCADE, related_name='values')
    value = models.DecimalField(max_digits=8, decimal_places=1)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.attribute.description} value for {self.apartment_sensor}: {self.value}'

    @classmethod
    def list_for_user(cls, user):
        return cls.objects.filter(apartment_sensor__apartment__user=user)


class Sensor(models.Model):
    """
    Represents a physical product model. Eg. Elsys ERS-CO2

    Further capabilities of the product are defined by attributes.
    """

    name = models.CharField(max_length=64)
    description = models.TextField(max_length=512)
    provides = models.ManyToManyField('SensorAttribute', related_name='sensors')

    def __str__(self):
        return f'{self.name}'


UI_TYPE_CHOICES = (
    ('TEMPERATURE', 'Temperature'),
    ('HUMIDITY', 'Humidity'),
    ('CO2', 'Co2'),
    (None, 'Other'),
)


class SensorAttribute(models.Model):
    """
    Represent one capability of a sensor, eg. temperature.
    """

    uri = models.CharField(max_length=255)
    description = models.CharField(max_length=128)
    ui_type = models.CharField(max_length=128, null=True, choices=UI_TYPE_CHOICES)

    def __str__(self):
        return self.description or self.uri

    class Meta:
        verbose_name_plural = "Sensor Attributes"


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
        'SensorAttribute', related_name='services',
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
