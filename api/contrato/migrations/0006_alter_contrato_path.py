# Generated by Django 3.2.2 on 2021-05-13 16:42

from django.db import migrations, models
import pathlib


class Migration(migrations.Migration):

    dependencies = [
        ('contrato', '0005_alter_contrato_path'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contrato',
            name='path',
            field=models.FilePathField(blank=True, null=True, path=pathlib.PurePosixPath('/home/jsv/Documents/CARRERA/tfg4/rasa-chatbot/api/media')),
        ),
    ]
