from django.db.models import Count
from .models import PurchaseOrder, SalesOrder

def get_order_item_count():
  orders = PurchaseOrder.objects.annotate(total_items=Count('item_sl'))
  return orders

def get_sorder_item_count():
  orders = SalesOrder.objects.annotate(total_items=Count('item_sl'))
  return orders
