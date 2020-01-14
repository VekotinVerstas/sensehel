from django.db import transaction
from rest_framework import serializers

from .. import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ('username', 'first_name', 'last_name', 'phone')
        read_only_fields = fields


class ServiceSerializer(serializers.HyperlinkedModelSerializer):
    requires = serializers.SlugRelatedField(many=True, read_only=True, slug_field='uri')

    class Meta:
        model = models.Service
        fields = (
            'id',
            'name',
            'description',
            'price',
            'benefit_short',
            'benefit_long',
            'eula_url',
            'img_logo_url',
            'img_service_url',
            'report_url',
            'preview_url',
            'requires'
        )


class SensorAttributeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.SensorAttribute
        fields = ('uri', 'description', 'ui_type')
        read_only_fields = fields


class SensorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Sensor
        fields = ('id', 'name', 'description', 'provides')
        read_only_fields = fields


class BasicSensorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Sensor
        fields = ('id', 'name', 'description')
        read_only_fields = fields


class ApartmentSensorValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ApartmentSensorValue
        fields = ('value', 'updated_at')


class ApartmentSensorAttributeSerializer(serializers.ModelSerializer):
    description = serializers.CharField(source='attribute.description')
    uri = serializers.CharField(source='attribute.uri')
    ui_type = serializers.CharField(source='attribute.ui_type')
    value = serializers.IntegerField(source='latest_value.value')
    updated_at = serializers.DateTimeField(source='latest_value.updated_at')

    class Meta:
        model = models.ApartmentSensorAttribute
        fields = ('id', 'description', 'uri', 'ui_type', 'value', 'updated_at')


class ApartmentSensorSerializer(serializers.ModelSerializer):
    attributes = ApartmentSensorAttributeSerializer(many=True, read_only=True)
    sensor = BasicSensorSerializer()

    class Meta:
        model = models.ApartmentSensor
        fields = ('id', 'attributes', 'identifier', 'sensor')


class ApartmentSerializer(serializers.HyperlinkedModelSerializer):
    apartment_sensors = ApartmentSensorSerializer(many=True)

    class Meta:
        model = models.Apartment
        fields = ('id', 'street', 'city', 'postal_code', 'apartment_sensors')


class CreateSubscriptionSerializer(serializers.ModelSerializer):
    include_history = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = models.Subscription
        fields = ('service', 'attributes', 'include_history')

    def create(self, validated_data):
        include_history = validated_data.pop('include_history', False)
        with transaction.atomic():
            subscription = super().create(dict(user=self.context['request'].user, **validated_data))
            subscription.create_in_service()
        if include_history:
            subscription.submit_history()
        return subscription


class SubscriptionSerializer(serializers.HyperlinkedModelSerializer):
    service = ServiceSerializer()

    class Meta:
        model = models.Subscription
        fields = ('id', 'uuid', 'created_at', 'updated_at', 'service')
