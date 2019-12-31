from django.conf.urls import url
from rest_framework import routers
from rest_framework.schemas import get_schema_view

from . import views

router = routers.DefaultRouter()
router.register(r'sensors', views.SensorViewSet)
router.register(r'sensorattributes', views.SensorAttributeViewSet)
router.register(r'services', views.ServiceViewSet)
router.register(r'apartments', views.ApartmentViewSet, base_name='apartment-list')
router.register(r'users', views.UserViewSet, base_name='user-list')
router.register(
    r'subscriptions', views.SubscriptionViewSet, base_name='subscriptions-list'
)
router.register(r'apartmentsensors', views.ApartmentSensorViewSet)
router.register(r'apartmentsensorvalues', views.ApartmentSensorValueViewSet)

schema_view = get_schema_view(title='SenseHel API')

# APIView does not and should not mix with routers
urls = [
    url(r'schema/', schema_view),
    url(r'available-services', views.ApartmentServiceList.as_view(), name='available-services'),
    url(r'update-sensor-by-identifier', views.update_sensor_by_identifier),
    url(r'digita-gw', views.digita_gw, name='digita-gw'),
]

urlpatterns = router.urls + urls
