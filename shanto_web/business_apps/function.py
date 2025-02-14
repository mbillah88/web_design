from django.db.models import Count
from .models import PurchaseOrder

def get_order_item_count():
  orders = PurchaseOrder.objects.annotate(total_items=Count('item_sl'))
  return orders
