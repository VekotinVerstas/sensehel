from django.db import models


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