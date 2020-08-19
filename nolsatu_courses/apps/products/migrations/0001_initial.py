# Generated by Django 2.2.6 on 2020-08-19 04:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('courses', '0041_auto_20200721_1054'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=50, unique=True)),
                ('status', models.SmallIntegerField(choices=[(1, 'Created'), (2, 'Success'), (3, 'Pending'), (4, 'Failed'), (5, 'Expired')], default=1)),
                ('tax', models.IntegerField(blank=True, null=True, verbose_name='Pajak')),
                ('discount', models.IntegerField(blank=True, null=True, verbose_name='Diskon')),
                ('grand_total', models.BigIntegerField(blank=True, null=True, verbose_name='Grand Total')),
                ('remote_transaction_id', models.CharField(blank=True, max_length=220, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.IntegerField(verbose_name='Harga')),
                ('code', models.CharField(blank=True, max_length=50, null=True, verbose_name='Kode')),
                ('discount_type', models.SmallIntegerField(blank=True, choices=[(1, 'Persentase'), (2, 'Nilai')], null=True, verbose_name='Diskon Tipe')),
                ('discount_value', models.IntegerField(blank=True, null=True, verbose_name='Nilai Diskon')),
                ('discount', models.IntegerField(blank=True, null=True, verbose_name='Diskon')),
                ('course', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='courses.Courses', verbose_name='Kursus')),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.IntegerField(verbose_name='Harga')),
                ('name', models.CharField(max_length=220, verbose_name='Nama')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.Order', verbose_name='Pesanan')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.Product', verbose_name='Produk')),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.Product', verbose_name='Produk')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
        ),
    ]
