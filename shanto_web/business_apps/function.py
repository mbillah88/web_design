from django.db.models import Count
from .models import *

def get_order_item_count():
  orders = PurchaseOrder.objects.annotate(total_items=Count('items'))
  return orders
