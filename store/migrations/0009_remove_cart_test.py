# Generated by Django 5.1.4 on 2024-12-17 01:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_rename_ids_cart_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='test',
        ),
    ]
