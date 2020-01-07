from django.conf.urls import url
from rest_framework import routers
from rest_framework.schemas import get_schema_view

from . import views

router = routers.DefaultRouter()
router.register(r'sensors', views.SensorViewSet)
router.register(r'sensorattributes', views.SensorAttributeViewSet)
router.register(r'services', views.ServiceViewSet)
router.register(r'apartments', views.ApartmentViewSet, base_name='apartment-list')
router.register(r'subscriptions', views.SubscriptionViewSet)
router.register(r'apartmentsensors', views.ApartmentSensorViewSet)

schema_view = get_schema_view(title='SenseHel API')

# APIView does not and should not mix with routers
urls = [
    url(r'schema/', schema_view),
    url(r'available-services', views.AvailableServicesList.as_view(), name='available-services'),
    url(r'digita-gw', views.digita_gw, name='digita-gw'),
]

urlpatterns = router.urls + urls
