# Generated by Django 5.2 on 2025-06-09 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_order_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='phone',
            field=models.CharField(max_length=30),
        ),
    ]
