# Generated by Django 3.2.2 on 2021-05-12 02:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrato', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contrato',
            name='vendor_surname',
        ),
        migrations.AddField(
            model_name='contrato',
            name='buyer_address',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name='contrato',
            name='buyer_dni',
            field=models.CharField(blank=True, max_length=9),
        ),
        migrations.AddField(
            model_name='contrato',
            name='buyer_name',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='contrato',
            name='buyer_province',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='contrato',
            name='buyer_signature',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='contrato',
            name='court',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='contrato',
            name='insurance_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='contrato',
            name='vehicle_brand',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='contrato',
            name='vehicle_chassis_nb',
            field=models.CharField(blank=True, max_length=8),
        ),
        migrations.AddField(
            model_name='contrato',
            name='vehicle_kms',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='contrato',
            name='vehicle_plate',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='contrato',
            name='vehicle_value',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='contrato',
            name='vendor_signature',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='contrato',
            name='vendor_name',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
