# Generated by Django 4.2.11 on 2024-05-14 02:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bd', '0006_delete_tokendeautenticacion_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='validaToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tokens', models.CharField(max_length=6)),
                ('tiempo', models.TimeField()),
            ],
        ),
    ]
