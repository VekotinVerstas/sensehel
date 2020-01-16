import binascii
import logging

from django.conf import settings
from rest_framework import generics, status, viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from core.utils.elsys import decode_elsys_payload

from . import serializers
from .. import models

log = logging.getLogger(__name__)


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Service.objects.all()
    serializer_class = serializers.ServiceSerializer


class ApartmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Serialize Apartments current authenticated user belongs to.
    """
    serializer_class = serializers.ApartmentSerializer
    queryset = models.Apartment.objects.none()  # For inspection only; get_queryset is used live

    def get_queryset(self):
        return self.request.user.apartments.all()


class ApartmentSensorViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ApartmentSensorSerializer
    queryset = models.ApartmentSensor.objects.none()  # For inspection only; get_queryset is used live

    def get_queryset(self):
        return models.ApartmentSensor.list_for_user(self.request.user)


class AvailableServicesList(generics.ListAPIView):
    """
    Serialize all services current authenticated user could
    subscribe to considering what sensors are available and what
    requirements services have.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.ServiceSerializer

    def get_queryset(self):
        return models.Service.list_available_for_user(self.request.user)


class SensorViewSet(viewsets.ModelViewSet):
    queryset = models.Sensor.objects.all()
    serializer_class = serializers.SensorSerializer


class SensorAttributeViewSet(viewsets.ModelViewSet):
    queryset = models.SensorAttribute.objects.all()
    serializer_class = serializers.SensorAttributeSerializer


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

    def perform_destroy(self, instance):
        instance.delete_in_service()
        instance.delete()


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def digita_gw(request):
    """
    Digita GW endpoint implementation
    """
    identifier = request.data['DevEUI_uplink']['DevEUI']
    apsen = models.ApartmentSensor.objects.get_or_create(identifier=identifier)[0]
    payload = binascii.unhexlify(request.data['DevEUI_uplink']['payload_hex'])
    decoded_payload = decode_elsys_payload(payload)
    mapping = settings.DIGITA_GW_PAYLOAD_TO_ATTRIBUTES  # type: dict

    new_values = []
    for key, value in decoded_payload.items():
        uri = mapping.get(key, '')
        if uri:
            attr = models.SensorAttribute.objects.get_or_create(uri=uri, defaults={'description': key})[0]
        else:
            attr = models.SensorAttribute.objects.get_or_create(description=key)[0]
        apsen_attr = apsen.attributes.get_or_create(attribute=attr)[0]
        new_values.append(apsen_attr.values.create(value=value))
    models.Subscription.handle_new_values(new_values)
    return Response({"message": "Updated successfully"})
