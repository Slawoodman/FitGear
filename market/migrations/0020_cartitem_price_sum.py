# Generated by Django 3.2.18 on 2024-04-14 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0019_rename_discounted_price_product_old_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='price_sum',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
