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

class ItemProduct(models.Model):
  item_name = models.CharField(max_length=255)
  category_name = models.ForeignKey(ItemCategory, on_delete=models.CASCADE, null = True)
  brand_name = models.ForeignKey(ItemBrand, on_delete=models.CASCADE, null = True)
  item_model = models.CharField(max_length=255, null = True, default='')
  item_description = models.CharField(max_length=255, null = True, default='')
  itme_unit = models.CharField(max_length=255, null = True, blank =True)
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
