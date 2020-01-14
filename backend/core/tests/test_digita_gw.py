from django.urls import reverse
from rest_framework.test import APITestCase

from core.models import Apartment, ApartmentSensor, Sensor
from .data import sensor_data_package


class DigitaTest(APITestCase):
    url = reverse('digita-gw')

    def test_new_sensor_gw_data(self):
        # No sensor
        response = self.client.post(self.url, sensor_data_package, format='json')
        self.assertEqual(200, response.status_code)
        self.assertTrue(ApartmentSensor.objects.filter(identifier="A81758FFFE030CF6").exists())

    def test_valid_gw_data(self):
        sensor = Sensor.objects.create(name="T-800")
        apartment = Apartment.objects.create()
        ApartmentSensor.objects.create(
            apartment=apartment, sensor=sensor, identifier="A81758FFFE030CF6"
        )
        response = self.client.post(self.url, sensor_data_package, format='json')
        self.assertEqual(200, response.status_code)
