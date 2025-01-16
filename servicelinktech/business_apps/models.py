from django.db import models
from django.contrib.auth.models import User
import datetime
from django.utils import timezone

# Create your models here.
def imageFilePath(request, filename):
    old_filename = filename
    timeNow = datetime.datetime.now()
    filename = "%s%s" % (timeNow, old_filename)
    return BASE_DIR('uploads/', filename)
  
class ItemCategory(models.Model):
  category_name = models.CharField(max_length=255)
  category_description = models.CharField(max_length=255)
  cat_image = models.ImageField(upload_to='images/category/', default='images/default.png')
  #created_at = models.DateTimeField()      
  def __str__(self):         
    return self.category_name

class ItemBrand(models.Model):
  brand_name = models.CharField(max_length=255)
  brand_description = models.CharField(max_length=255)
  brand_image = models.ImageField(upload_to='images/brand/', default='images/default.png')
  def __str__(self):         
    return self.brand_name

class ItemProduct(models.Model):
  item_name = models.CharField(max_length=255)
  category_name = models.ForeignKey(ItemCategory, on_delete=models.CASCADE, null = True)
  brand_name = models.ForeignKey(ItemBrand, on_delete=models.CASCADE, null = True)
  item_model = models.CharField(max_length=255, null = True)
  item_description = models.CharField(max_length=255, null = True)
  itme_unit = models.CharField(max_length=255, null = True, blank =True)
  itme_sku = models.CharField(max_length=255, null = True, blank =True)
  itme_alert_qty = models.CharField(max_length=255, null = True, blank =True)
  itme_barcode = models.CharField(max_length=255, null = True, blank =True)
  item_sprice = models.DecimalField(max_digits=10, decimal_places=2, null=True)
  item_pprice = models.DecimalField(max_digits=10, decimal_places=2, null=True)
  item_image = models.ImageField(upload_to='images/product/', blank=True, null=True, default='images/default.png')
  itme_status = models.CharField(max_length=255, null = True, blank =True)
  created_at = models.DateTimeField(auto_now_add=True, null = True)   
  def __str__(self):         
    return self.item_name

class Clients(models.Model):
  client_name = models.CharField(max_length=255)
  client_org = models.CharField(max_length=255)
  client_desig = models.CharField(max_length=255)
  client_mobile = models.CharField(max_length=255)
  client_address = models.CharField(max_length=255)
  def __str__(self):         
    return self.client_name

class Supplier(models.Model):
  supplier_name = models.CharField(max_length=255)
  supplier_org = models.CharField(max_length=255)
  supplier_desig = models.CharField(max_length=255)
  supplier_mobile = models.CharField(max_length=255)
  supplier_address = models.CharField(max_length=400)
  def __str__(self):         
    return self.supplier_name

class PurchaseOrder(models.Model):
  supplier_id = models.ForeignKey(Supplier, on_delete=models.CASCADE, null = True)
  porder_total = models.DecimalField(max_digits=10, decimal_places=2, null=True)
  porder_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
  porder_status = models.CharField(max_length=255)
  porder_note = models.CharField(max_length=255)
  porder_create_time = models.DateTimeField(auto_now_add=True,null = True)  
  porder_update_time = models.DateTimeField(auto_now=True,null = True)  
  porder_create_by = models.ForeignKey(User, on_delete=models.CASCADE, null = True, related_name='o_create_user')
  porder_update_by = models.ForeignKey(User, on_delete=models.CASCADE, null = True, related_name='o_create_update')
  
  def __str__(self):
    return f'PurchaseOrder - {str(self.id)}'

class PurchaseOrderItem(models.Model):
  porder_id = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, null = True)
  item_id = models.ForeignKey(ItemProduct, on_delete=models.CASCADE, null = True)
  itme_unit = models.CharField(max_length=255)
  itme_qty = models.PositiveBigIntegerField(default=1)
  item_sprice = models.DecimalField(max_digits=10, decimal_places=2, null=True)
  item_pprice = models.DecimalField(max_digits=10, decimal_places=2, null=True)

  def __str__(self):
    return f'PurchaseDetails - {str(self.id)}'

class PurchasePayment(models.Model):
  order_id = models.ForeignKey(PurchaseOrderItem, on_delete=models.CASCADE, null = True)
  payment_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
  payment_status = models.CharField(max_length=255)
  payment_time = models.DateTimeField(auto_now_add=True, null = True)  
  payment_update_time = models.DateTimeField(auto_now=True, null = True)   
  payment_create_by = models.ForeignKey(User, on_delete=models.CASCADE, null = True, related_name='p_create_user')
  payment_update_by = models.ForeignKey(User, on_delete=models.CASCADE, null = True, related_name='p_create_update')