# Generated by Django 4.2.5 on 2024-07-01 02:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_remove_product_selling_price_category_description_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='paypal_payment_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
