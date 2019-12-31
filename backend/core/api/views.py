import binascii
import logging

from django.conf import settings
from rest_framework import generics, status, viewsets, permissions
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

from core.utils.elsys import decode_elsys_payload

from . import serializers
from .. import models

log = logging.getLogger(__name__)


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = models.Service.objects.all()
    serializer_class = serializers.ServiceSerializer


class ApartmentViewSet(viewsets.ModelViewSet):
    """
    Serialize Apartments current authenticated user belongs to.
    """

    serializer_class = serializers.ApartmentSerializer

    def get_queryset(self):
        return models.Apartment.objects.filter(user=self.request.user)


class UserViewSet(
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    Serialize all subscriptions and provide methods to create new
    subscriptions and terminate old ones.
    """

    serializer_class = serializers.UserSerializer

    def get_queryset(self):
        return models.User.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        self.request.user.delete()
        return Response({'message': 'Removed'}, status=status.HTTP_202_ACCEPTED)


class ApartmentSensorViewSet(viewsets.ModelViewSet):
    queryset = (
        models.ApartmentSensor.objects.all()
    )  # TODO: require user has access for this resource
    serializer_class = serializers.ApartmentSensorSerializer


class ApartmentSensorValueViewSet(viewsets.ModelViewSet):
    queryset = (
        models.ApartmentSensorValue.objects.all()
    )  # TODO: require user has access for this resource
    serializer_class = serializers.ApartmentSensorValueSerializer


class ApartmentServiceList(generics.ListAPIView):
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

    def get_queryset(self):
        return models.Subscription.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        # TODO: using serializers would be the right way ..

        # serializer = self.get_serializer(data=request.data)
        # serializer.is_valid(raise_exception=True)

        # headers = self.get_success_headers(serializer.data)
        # return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        service_id = int(request.data['service'])
        if models.Subscription.objects.filter(
            user=self.request.user, service_id=service_id
        ).exists():
            return Response(
                {"detail": "Subscription for this service exists"},
                status=status.HTTP_409_CONFLICT,
            )

        models.Subscription.objects.create(
            user=self.request.user, service_id=service_id
        )
        return Response({}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@authentication_classes((BasicAuthentication,))
def update_sensor_by_identifier(request):
    """
    Example payload::

        {
            "identifier": "ABCDEFGH",
            "attributes": [
                {
                    "URI": "http://finto.fi/afo/en/page/p4770",
                    "value": 200
                },
                {
                    "URI": "http://urn.fi/URN:NBN:fi:au:ucum:r73",
                    "value": 21
                }

            ]
        }
    """
    try:
        apsen = models.ApartmentSensor.objects.get(
            identifier=request.data['identifier']
        )

        for attr in request.data['attributes']:
            apsenval = apsen.apartment_sensor_values.get(
                attribute__uri=attr['URI']
            )  # type: models.ApartmentSensorValue
            apsenval.value = attr['value']
            apsenval.save()

        return Response({"message": "Updated successfully"})
    except models.ApartmentSensor.DoesNotExist:
        return Response(
            {"message": "ApartmentSensor does not exists with given identifier"},
            status=status.HTTP_404_NOT_FOUND,
        )
    except models.ApartmentSensorValue.DoesNotExist:
        return Response(
            {"message": "ApartmentSensorValue does not exists with given URI"},
            status=status.HTTP_404_NOT_FOUND,
        )


@permission_classes([permissions.AllowAny])
@api_view(['POST'])
def digita_gw(request):
    """
    Digita GW endpoint implementation
    """
    identifier = request.data['DevEUI_uplink']['DevEUI']
    apsen = models.ApartmentSensor.objects.get_or_create(identifier=identifier)[0]
    payload = binascii.unhexlify(request.data['DevEUI_uplink']['payload_hex'])
    decoded_payload = decode_elsys_payload(payload)
    mapping = settings.DIGITA_GW_PAYLOAD_TO_ATTRIBUTES  # type: dict

    for key, value in decoded_payload.items():
        uri = mapping.get(key, '')
        if uri:
            attr = models.SensorAttribute.objects.get_or_create(uri=uri, defaults={'description': key})[0]
        else:
            attr = models.SensorAttribute.objects.get_or_create(description=key)[0]
        apsen.apartment_sensor_values.create(value=value, attribute=attr)
    return Response({"message": "Updated successfully"})
