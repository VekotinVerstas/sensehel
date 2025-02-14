# Generated by Django 2.2.8 on 2019-12-31 14:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_auto_20190130_0833'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apartmentsensor',
            name='apartment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='apartment_sensors', to='core.Apartment'),
        ),
        migrations.AlterField(
            model_name='apartmentsensor',
            name='sensor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Sensor'),
        ),
    ]
