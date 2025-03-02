# Generated by Django 4.2.6 on 2025-03-02 21:57

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('business_apps', '0025_purchasepayment_payment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseorder',
            name='barcode',
            field=models.ImageField(blank=True, null=True, upload_to='images/barcode/'),
        ),
        migrations.CreateModel(
            name='PurchaseReturn',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('return_quantity', models.IntegerField()),
                ('return_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('reason', models.TextField()),
                ('purchase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='business_apps.purchaseorder')),
            ],
        ),
        migrations.CreateModel(
            name='PurchaseCancel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cancel_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('reason', models.TextField()),
                ('purchase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='business_apps.purchaseorder')),
            ],
        ),
    ]
