# Generated by Django 3.2.18 on 2024-04-11 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0012_product_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='short_description',
            field=models.TextField(blank=True, max_length=200, null=True),
        ),
    ]