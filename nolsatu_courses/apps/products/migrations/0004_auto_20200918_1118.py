# Generated by Django 2.2.13 on 2020-09-18 04:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_cart_is_select'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='products.Order', verbose_name='Pesanan'),
        ),
        migrations.AlterField(
            model_name='product',
            name='discount',
            field=models.IntegerField(default=0, verbose_name='Diskon'),
        ),
    ]
