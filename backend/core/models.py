from django.contrib.auth.models import AbstractUser
from django.db import models


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
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
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
        return f'Sensor in apartment {self.apartment}'


class ApartmentSensorValue(models.Model):
    """
    Stores last measured value from a sensor attribute
    """

    apartment_sensor = models.ForeignKey(
        ApartmentSensor,
        related_name='apartment_sensor_values',
        on_delete=models.CASCADE,
    )
    attribute = models.ForeignKey('SensorAttribute', on_delete=models.DO_NOTHING)
    value = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Sensor Value for {self.apartment_sensor.apartment} {self.attribute} {self.value}'


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
        return f'{self.uri} ({self.description})'

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
    eula_url = models.CharField(max_length=255)
    img_logo_url = models.CharField(max_length=255, null=True)
    img_service_url = models.CharField(max_length=255, null=True)
    requires = models.ManyToManyField('SensorAttribute', related_name='services')

    def __str__(self):
        return f'{self.name}'

    @classmethod
    def list_available_for_user(cls, user):
        return cls.objects.filter(requires__sensors__apartmentsensor__apartment__user=user).distinct()


class Subscription(models.Model):
    """
    User subscribes to a service
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'User {self.user} subscription for {self.service}'

    class Meta:
        unique_together = ('user', 'service')
