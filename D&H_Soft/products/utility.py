from datetime import timedelta
from django.utils import timezone

def check_warranty_expiry(product, purchase_date):
    duration = product.warranty.duration_days if product.warranty else product.warranty_duration_months * 30
    expiry_date = purchase_date + timedelta(days=duration)
    remaining = (expiry_date - timezone.now()).days

    if remaining < 0:
        return "❌ মেয়াদ শেষ"
    elif remaining <= 7:
        return f"⚠️ {remaining} দিন বাকি"
    else:
        return f"✅ {remaining} দিন বাকি"
