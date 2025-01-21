# Generated by Django 4.2.6 on 2025-01-20 19:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop_apps', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Clients',
        ),
        migrations.RemoveField(
            model_name='purchaseorderitem',
            name='item_id',
        ),
        migrations.RemoveField(
            model_name='purchaseorderitem',
            name='porder_id',
        ),
        migrations.RemoveField(
            model_name='purchasepayment',
            name='order_id',
        ),
        migrations.RemoveField(
            model_name='purchasepayment',
            name='payment_create_by',
        ),
        migrations.RemoveField(
            model_name='purchasepayment',
            name='payment_update_by',
        ),
        migrations.DeleteModel(
            name='PurchaseOrder',
        ),
        migrations.DeleteModel(
            name='PurchaseOrderItem',
        ),
        migrations.DeleteModel(
            name='PurchasePayment',
        ),
        migrations.DeleteModel(
            name='Supplier',
        ),
    ]