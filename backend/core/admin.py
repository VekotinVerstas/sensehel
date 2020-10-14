from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count, Avg, Min, Max

from .models import (Apartment, ApartmentSensor, ApartmentSensorValue, Sensor,
                     SensorAttribute, Service, Subscription, User, ApartmentSensorAttribute, CustomReportService,
                     CustomReportSubscription)


class MyUserAdmin(UserAdmin):
    model = User

    fieldsets = UserAdmin.fieldsets + (('Contact', {'fields': ('phone',)}),)


class ApartmentSensorInline(admin.TabularInline):
    model = ApartmentSensor


class ApartmentSensorAdmin(admin.ModelAdmin):
    list_display = ['identifier', 'apartment', 'sensor', 'attributes']

    def attributes(self, ap_sensor):
        return list(SensorAttribute.objects\
            .filter(apartment_sensor_attributes__apartment_sensor=ap_sensor)\
            .values_list('description', flat=True).distinct())


class ApartmentSensorAttributeAdmin(admin.ModelAdmin):
    list_display = ['apartment_sensor', 'attribute', 'values', 'min', 'avg', 'max']
    list_filter = ['attribute']
    search_fields = ['apartment_sensor__identifier']

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            values_count=Count('values'),
            min=Min('values__value'),
            avg=Avg('values__value'),
            max=Max('values__value')
        )

    def values(self, attr):
        return attr.values_count

    def min(self, attr):
        return '%s' % float('%.4g' % attr.min)

    def avg(self, attr):
        return '%s' % float('%.4g' % attr.avg)

    def max(self, attr):
        return '%s' % float('%.4g' % attr.max)


class SensorAttributeAdmin(admin.ModelAdmin):
    list_display = ['description', 'uri', 'apartment_sensors']

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(apartment_sensors=Count('apartment_sensor_attributes'))

    def apartment_sensors(self, attr):
        return attr.apartment_sensors


class ApartmentAdmin(admin.ModelAdmin):
    inlines = [ApartmentSensorInline]


class ApartmentSensorValueAdmin(admin.ModelAdmin):
    list_display = ('apartment_sensor_attribute', 'value', 'updated_at')
    list_filter = ('apartment_sensor_attribute__attribute', )
    search_fields = ['apartment_sensor__identifier']
    date_hierarchy = 'updated_at'


admin.site.register(Apartment, ApartmentAdmin)
admin.site.register(ApartmentSensor, ApartmentSensorAdmin)
admin.site.register(ApartmentSensorAttribute, ApartmentSensorAttributeAdmin)
admin.site.register(Sensor)
admin.site.register(ApartmentSensorValue, ApartmentSensorValueAdmin)
admin.site.register(Service)
admin.site.register(Subscription)
admin.site.register(SensorAttribute, SensorAttributeAdmin)
admin.site.register(User, MyUserAdmin)

admin.site.register(CustomReportService)
admin.site.register(CustomReportSubscription)
