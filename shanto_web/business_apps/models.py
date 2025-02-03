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
  
# iterable 
OrderChoice =( 
    ("1", "Received"), 
    ("2", "Pending"), 
    ("3", "Ordered"), 
    ("4", "Cancel"), 
) 

class ItemCategory(models.Model):
  category_name = models.CharField(max_length=255)
  category_description = models.CharField(max_length=255, default='')
  cat_image = models.ImageField(upload_to='images/category/', default='images/default.png')
  #created_at = models.DateTimeField()      
  def __str__(self):         
    return self.category_name

class ItemBrand(models.Model):
  brand_name = models.CharField(max_length=255)
  brand_description = models.CharField(max_length=255, default='')
  brand_image = models.ImageField(upload_to='images/brand/', default='images/default.png')
  def __str__(self):         
    return self.brand_name

# Setting Tools .........
class ItemUnit(models.Model):
  unit_name = models.CharField(max_length=20)
  unit_description = models.CharField(max_length=100, default='Default')
  def __str__(self):         
    return self.unit_name

class ItemProduct(models.Model):
  item_name = models.CharField(max_length=255)
  category_name = models.ForeignKey(ItemCategory, on_delete=models.CASCADE, null = True)
  brand_name = models.ForeignKey(ItemBrand, on_delete=models.CASCADE, null = True)
  item_model = models.CharField(max_length=255, null = True, default='')
  item_description = models.CharField(max_length=255, null = True, default='')
  itme_unit = models.ForeignKey(ItemUnit, on_delete=models.CASCADE, null = True)
  itme_sku = models.CharField(max_length=255, null = True, blank =True, default='')
  itme_alert_qty = models.CharField(max_length=255, null = True, blank =True, default=0)
  itme_barcode = models.CharField(max_length=255, null = True, blank =True, default='')
  item_sprice = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0)
  item_pprice = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0)
  item_image = models.ImageField(upload_to='images/product/', blank=True, null=True, default='images/default.png')
  itme_status = models.CharField(max_length=255, null = True, blank =True, default='')
  created_at = models.DateTimeField(auto_now_add=True, null = True)   
  def __str__(self):         
    return self.item_name

class Clients(models.Model):
  client_name = models.CharField(max_length=255)
  client_org = models.CharField(max_length=100, default='')
  client_desig = models.CharField(max_length=100, default='')
  client_mobile = models.CharField(max_length=20, default='')
  client_address = models.CharField(max_length=255, default='')
  def __str__(self):         
    return self.client_name

class Supplier(models.Model):
  supplier_name = models.CharField(max_length=255)
  supplier_org = models.CharField(max_length=100, default='Slef')
  supplier_desig = models.CharField(max_length=100, default='Slef')
  supplier_mobile = models.CharField(max_length=20, default='')
  supplier_address = models.CharField(max_length=400, default='Slef')
  def __str__(self):         
    return self.supplier_name

class PurchaseOrder(models.Model):
  supplier_id = models.ForeignKey(Supplier, on_delete=models.CASCADE, null = True)
  porder_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0)
  porder_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0)
  porder_status = models.CharField(max_length=1,choices=OrderChoice, default=3)
  porder_note = models.CharField(max_length=500, default='')
  porder_create_time = models.DateTimeField(auto_now_add=True,null = True)  
  porder_update_time = models.DateTimeField(auto_now=True,null = True)  
  porder_create_by = models.ForeignKey(User, on_delete=models.CASCADE, null = True, related_name='o_create_user')
  porder_update_by = models.ForeignKey(User, on_delete=models.CASCADE, null = True, related_name='o_create_update')
  
  def __str__(self):
    return f'PurchaseOrder {self.id} by {self.supplier_id}'

class PurchaseOrderItem(models.Model):
  porder_id = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, null = True)
  item_id = models.ForeignKey(ItemProduct, on_delete=models.CASCADE, null = True)
  itme_qty = models.PositiveBigIntegerField(default=1)
  item_pprice = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0)

  def get_total_price(self):
    return self.itme_qty * self.porder_id.item_pprice

class PurchasePayment(models.Model):
  order_id = models.ForeignKey(PurchaseOrderItem, on_delete=models.CASCADE, null = True)
  payment_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0)
  payment_status = models.CharField(max_length=20)
  payment_time = models.DateTimeField(auto_now_add=True, null = True)  
  payment_update_time = models.DateTimeField(auto_now=True, null = True)   
  payment_create_by = models.ForeignKey(User, on_delete=models.CASCADE, null = True, related_name='p_create_user')
  payment_update_by = models.ForeignKey(User, on_delete=models.CASCADE, null = True, related_name='p_create_update')