from rest_framework.test import APITestCase

from core.models import (Apartment, ApartmentSensor, ApartmentSensorValue,
                         Sensor, SensorAttribute, User)


class ApartmentSensorTest(APITestCase):
    def setUp(self):
        user = User.objects.create_user(username="nkha", password="123456")
        sensor = Sensor.objects.create(name="T-800")
        apartment = Apartment.objects.create(user=user)
        apartment_sensor = ApartmentSensor.objects.create(
            apartment=apartment, sensor=sensor, identifier="A81758FFFE030CF6"
        )
        attribute = SensorAttribute.objects.create(
            uri='test uri', description='test description'
        )
        ApartmentSensorValue.objects.create(
            apartment_sensor_attribute=apartment_sensor.attributes.create(attribute=attribute),
            value=12)

    def test_sensor_attribute(self):
        # Without logged in user
        response = self.client.get('/api/sensorattributes/')
        self.assertEqual(401, response.status_code)

        # With logged in user
        self.client.login(username="nkha", password="123456")
        response = self.client.get('/api/sensorattributes/')
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data[0]['uri'], 'test uri')
        self.assertEqual(response.data[0]['description'], 'test description')
