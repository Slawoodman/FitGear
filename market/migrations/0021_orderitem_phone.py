# Generated by Django 3.2.18 on 2024-04-15 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0020_cartitem_price_sum'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='phone',
            field=models.CharField(default='', max_length=20),
        ),
    ]
