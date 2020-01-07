import requests
from django.urls import reverse
from rest_framework import serializers

from core import models
from core.tests.base import SenseHelAPITestCase


class MockSubscriptionRequests:
    def __enter__(self):
        def post(_self, *args, **kwargs):
            self.last_request = (args, kwargs)
            resp = requests.Response()
            resp.status_code = 200
            return resp

        self.old_post = models.Subscription._post  # noqa
        models.Subscription._post = post

    def __exit__(self, *args):
        models.Subscription._post = self.old_post


class SubscriptionTest(SenseHelAPITestCase):
    mock_requests = MockSubscriptionRequests()

    def setUp(self):
        self.temperature = models.SensorAttribute.objects.create(description='temperature', uri='uri://temperature')
        self.service = models.Service.objects.create(
            subscribe_url='https://service.com/api/subscriptions/',
            data_url='https://service.com/api/measurements/')
        self.service.requires.add(self.temperature)

        self.user = models.User.objects.create()
        self.apartment = self.user.apartments.create()
        self.apsen = self.apartment.apartment_sensors.create()

        self.url = reverse('subscription-list')

    def test_subscribe_with_no_logged_in_user(self):
        # Given that no user is logged in
        # When requesting to create a new subscription
        response = self.client.post(self.url)

        # Then a 401 response is returned
        self.assertEqual(401, response.status_code)

    def test_subscribe_with_no_attributes(self):
        # Given that a user is logged in
        self.client.force_login(self.user)

        # When requesting to create a new subscription without supplying any attributes for which to subscribe
        response = self.client.post(self.url, {'service': self.service.id})

        # Then a 400 response is returned
        self.assertEqual(400, response.status_code)

    def test_subscribe(self):
        # Given that a user with an apartment sensor with appropriate attributes is logged in
        self.client.force_login(self.user)
        apsen_attr = self.apsen.attributes.create(attribute=self.temperature)

        # When requesting to create a new subscription, supplying the attributes for which to subscribe
        with self.mock_requests:
            response = self.client.post(self.url, {'service': self.service.id, 'attributes': [apsen_attr.id]})

        # Then a 201 response is returned
        self.assertEqual(201, response.status_code)

        # And a new subscription is created in the db
        subscription = models.Subscription.objects.get()

        # And the subscription is submitted to the external service
        ([url], kwargs) = self.mock_requests.last_request
        self.assertEqual(url, self.service.subscribe_url)
        self.assert_dict_contains(kwargs['data'], {
            'uuid': str(subscription.uuid),
            'attributes': [{
                'id': self.temperature.id,
                'uri': self.temperature.uri,
                'description': self.temperature.description}],
            'auth_token': str(self.service.auth_token)})

    def test_subscribe_with_history(self):
        # Given that a user with an apartment sensor with appropriate attributes is logged in
        self.client.force_login(self.user)
        apsen_attr = self.apsen.attributes.create(attribute=self.temperature)

        # And given that some measurements have already been stored for the sensor
        value = apsen_attr.values.create(value=22)

        # When requesting to create a new subscription, including history
        with self.mock_requests:
            response = self.client.post(self.url, {
                'service': self.service.id,
                'attributes': [apsen_attr.id],
                'include_history': True})

        # Then a 201 response is returned
        self.assertEqual(201, response.status_code)

        # And a new subscription is created in the db
        subscription = models.Subscription.objects.get()

        # And the existing measurements are submitted to the external service
        ([url], kwargs) = self.mock_requests.last_request
        self.assertEqual(url, self.service.data_url)
        data = kwargs['data']
        self.assert_dict_contains(data, {
            'uuid': str(subscription.uuid),
            'values': [{
                'attribute': apsen_attr.id,
                'timestamp': serializers.DateTimeField().to_representation(value.updated_at),
                'value': value.value}],
            'auth_token': str(self.service.auth_token)})
