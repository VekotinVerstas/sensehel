from django.urls import reverse
from rest_framework.test import APITestCase

from core.models import SensorAttribute, Service, User, ApartmentSensor


class ServiceTest(APITestCase):
    def test_available_services_with_no_logged_in_user(self):
        # Given that no user is logged in
        # When requesting the list of available services
        response = self.client.get(reverse('available-services'))

        # Then a 401 response is returned
        self.assertEqual(401, response.status_code)

    def test_available_services_with_no_apartment(self):
        # Given that a user with no linked apartment is logged in
        user = User.objects.create(username="HomerHomeless")
        self.client.force_login(user)

        # When requesting the list of available services
        response = self.client.get(reverse('available-services'))

        # Then a 200 response is returned
        self.assertEqual(200, response.status_code)

        # And it contains an empty list
        self.assertEqual(len(response.data), 0)

    def test_available_services_with_no_sensors(self):
        # Given that a user with an apartment but no sensors is logged in
        user = User.objects.create(username="CedrikSenseless")
        user.apartment_set.create()
        self.client.force_login(user)

        # When requesting the list of available services
        response = self.client.get(reverse('available-services'))

        # Then a 200 response is returned
        self.assertEqual(200, response.status_code)

        # And it contains an empty list
        self.assertEqual(len(response.data), 0)

    def test_available_services(self):
        # Given that a user with an apartment is logged in
        user = User.objects.create(username="CedrikSensei")
        apartment = user.apartment_set.create()
        self.client.force_login(user)

        # And given that there are available services related to the sensors in the user's apartment
        service = Service.objects.create(name='Big Brother')
        attr = SensorAttribute.objects.create(description='Camera')
        ApartmentSensor.objects.create(apartment=apartment, sensor=attr.sensors.create())
        service.requires.set([attr])

        # When requesting the list of available services
        response = self.client.get(reverse('available-services'))

        # Then a 200 response is returned
        self.assertEqual(200, response.status_code)

        # And it contains the available service
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Big Brother')
