from django.db import models

from .user import User


class Apartment(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='apartments')
    street = models.CharField(max_length=64)
    city = models.CharField(max_length=32)
    postal_code = models.CharField(max_length=10)

    def __str__(self):
        return f'{self.user.name()} - {self.street} ({self.postal_code})'


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