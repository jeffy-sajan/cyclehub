# Generated by Django 5.0.6 on 2024-11-09 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cycle', '0004_remove_cartitem_cart_remove_cartitem_product_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='stock',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
