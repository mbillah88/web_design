# Generated by Django 4.2.6 on 2025-01-16 08:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('business_apps', '0003_purchaseorder_itemproduct_itme_alert_qty_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='purchaseorder',
            old_name='supplier_name',
            new_name='supplier_id',
        ),
        migrations.AlterField(
            model_name='purchaseorder',
            name='porder_create_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='o_create_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='purchaseorder',
            name='porder_update_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='o_create_update', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='purchasepayment',
            name='payment_create_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='p_create_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='purchasepayment',
            name='payment_update_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='p_create_update', to=settings.AUTH_USER_MODEL),
        ),
    ]
