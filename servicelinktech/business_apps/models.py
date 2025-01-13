from django.db import models
import datetime

# Create your models here.
def imageFilePath(request, filename):
    old_filename = filename
    timeNow = datetime.datetime.now()
    filename = "%s%s" % (timeNow, old_filename)
    return BASE_DIR('uploads/', filename)

class ItemCategory(models.Model):
  category_name = models.CharField(max_length=255)
  category_description = models.CharField(max_length=255)
  cat_image = models.ImageField(upload_to='images/category/')
  #created_at = models.DateTimeField()      
  def __str__(self):         
    return self.category_name


class ItemBrand(models.Model):
  brand_name = models.CharField(max_length=255)
  brand_description = models.CharField(max_length=255)
  brand_image = models.ImageField(upload_to='images/brand/')
  category_name = models.ForeignKey(ItemCategory, on_delete=models.CASCADE, null = True)   
  def __str__(self):         
    return self.brand_name


class ItemProduct(models.Model):
  item_name = models.CharField(max_length=255)
  item_model = models.CharField(max_length=255, null = True)
  item_description = models.CharField(max_length=255, null = True)
  item_sprice = models.DecimalField(max_digits=10, decimal_places=2, null=True)
  item_pprice = models.DecimalField(max_digits=10, decimal_places=2, null=True)
  item_image = models.ImageField(upload_to='images/product/', blank=True, null=True)
  category_name = models.ForeignKey(ItemCategory, on_delete=models.CASCADE, null = True)
  brand_name = models.ForeignKey(ItemBrand, on_delete=models.CASCADE, null = True)
  created_at = models.DateTimeField(null = True)   
  def __str__(self):         
    return self.item_name