# accounts/signals.py
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from accounts.models import CustomUser, Profile, Role
from products.models import PurchasePayment, SalePayment, ExpensePayment, RefundPayment

@receiver(post_save, sender=PurchasePayment)
@receiver(post_save, sender=SalePayment)
@receiver(post_save, sender=ExpensePayment)
@receiver(post_save, sender=RefundPayment)
def log_payment_save(sender, instance, created, **kwargs):
    PaymentAudit.objects.create(
        payment_type=sender.__name__,
        payment_id=instance.id,
        action='created' if created else 'updated',
        performed_by=instance.updated_by or instance.created_by
    )

@receiver(pre_delete, sender=PurchasePayment)
@receiver(pre_delete, sender=SalePayment)
@receiver(pre_delete, sender=ExpensePayment)
@receiver(pre_delete, sender=RefundPayment)
def log_payment_delete(sender, instance, **kwargs):
    PaymentAudit.objects.create(
        payment_type=sender.__name__,
        payment_id=instance.id,
        action='deleted',
        performed_by=instance.deleted_by
    )
    # apps.py এ দিতে হবে....
    #def ready(self):
    #    import accounts.signals  # ✅ Import signal here
