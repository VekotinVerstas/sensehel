import binascii
import logging

from django.conf import settings
from requests import HTTPError
from rest_framework import generics, status, viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

import core.models.apartment_sensor_models
import core.models.sensor_models
import core.models.service
from core.utils.elsys import decode_elsys_payload

from . import serializers
from .. import models

log = logging.getLogger(__name__)


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = core.models.service.Service.objects.all()
    serializer_class = serializers.ServiceSerializer


class ApartmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Serialize Apartments current authenticated user belongs to.
    """
    serializer_class = serializers.ApartmentSerializer
    queryset = core.models.apartment_sensor_models.Apartment.objects.none()  # For inspection only; get_queryset is used live

    def get_queryset(self):
        return self.request.user.apartments.all()


class ApartmentSensorViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ApartmentSensorSerializer
    queryset = core.models.apartment_sensor_models.ApartmentSensor.objects.none()  # For inspection only; get_queryset is used live

    def get_queryset(self):
        return core.models.apartment_sensor_models.ApartmentSensor.list_for_user(self.request.user)


class AvailableServicesList(generics.ListAPIView):
    """
    Serialize all services current authenticated user could
    subscribe to considering what sensors are available and what
    requirements services have.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.ServiceSerializer

    def get_queryset(self):
        return core.models.service.Service.list_available_for_user(self.request.user)


class SensorViewSet(viewsets.ModelViewSet):
    queryset = core.models.sensor_models.Sensor.objects.all()
    serializer_class = serializers.SensorSerializer


class SensorAttributeViewSet(viewsets.ModelViewSet):
    queryset = core.models.sensor_models.SensorAttribute.objects.all()
    serializer_class = serializers.SensorAttributeSerializer


class AftereffectResponse(Response):
    def __init__(self, *args, **kwargs):
        self.aftereffect = kwargs.pop('aftereffect', None)
        return super().__init__(*args, **kwargs)

    def close(self):
        super().close()
        if self.aftereffect:
            self.aftereffect()


class SubscriptionViewSet(
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.CreateModelMixin,
    viewsets.mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    Serialize all subscriptions and provide methods to create new
    subscriptions and terminate old ones.
    """
    serializer_class = serializers.SubscriptionSerializer
    queryset = models.Subscription.objects.none()  # For inspection only; get_queryset is used live

    serializer_classes = {
        'create': serializers.CreateSubscriptionSerializer
    }

    def get_queryset(self):
        return models.Subscription.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.serializer_class)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        try:
            instance.delete_in_service()
        except HTTPError:
            return Response('Could not unsubscribe in service.', status=502)

        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            self.perform_create(serializer)
        except HTTPError:
            return Response('Could not register subscription with service.', status=502)

        headers = self.get_success_headers(serializer.data)
        return AftereffectResponse(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers,
            aftereffect=lambda: serializer.submit_history())


class CustomReportSubscriptionViewSet(viewsets.mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.CustomReportSubscriptionSerializer
    queryset = models.CustomReportSubscription.objects.none()  # For inspection only; get_queryset is used live

    def get_queryset(self):
        return models.CustomReportSubscription.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def digita_gw(request):
    """
    Digita GW endpoint implementation
    """
    try:
        identifier = request.data['DevEUI_uplink']['DevEUI']
    except KeyError:
        return Response({"message": "Message ignored"})
    apsen = core.models.apartment_sensor_models.ApartmentSensor.objects.get_or_create(identifier=identifier)[0]
    payload = binascii.unhexlify(request.data['DevEUI_uplink']['payload_hex'])
    decoded_payload = decode_elsys_payload(payload)
    mapping = settings.DIGITA_GW_PAYLOAD_TO_ATTRIBUTES  # type: dict

    new_values = []
    for key, value in decoded_payload.items():
        uri = mapping.get(key, '')
        if uri:
            attr = core.models.sensor_models.SensorAttribute.objects.get_or_create(uri=uri, defaults={'description': key})[0]
        else:
            attr = core.models.sensor_models.SensorAttribute.objects.get_or_create(description=key)[0]
        apsen_attr = apsen.attributes.get_or_create(attribute=attr)[0]
        new_values.append(apsen_attr.values.create(value=value))
    models.Subscription.handle_new_values(new_values)
    return Response({"message": "Updated successfully"})

