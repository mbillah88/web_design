from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(ItemCategory)
admin.site.register(ItemBrand)
admin.site.register(ItemProduct)
admin.site.register(Clients)
admin.site.register(Supplier)
admin.site.register(PurchaseOrder)
admin.site.register(PurchaseOrderItem)
admin.site.register(PurchasePayment)

