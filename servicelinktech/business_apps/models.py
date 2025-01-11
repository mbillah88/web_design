from django.db import models
import datetime

# Create your models here.
def imageFilePath(request, filename):
    old_filename = filename
    timeNow = datetime.datetime.now()
    filename = "%s%s" % (timeNow, old_filename)
    return os.path.join('uploads/', filename)

class ItemCategory(models.Model):
  category_name = models.CharField(max_length=255)
  category_description = models.CharField(max_length=255)
  cat_image = models.ImageField(upload_to='images/')
  #created_at = models.DateTimeField()      
  def __str__(self):         
    return self.title


class ItemBrand(models.Model):
  brand_name = models.CharField(max_length=255)
  brand_description = models.CharField(max_length=255)
  brand_image = models.ImageField(upload_to='images/')


class ItemProduct(models.Model):
  item_name = models.CharField(max_length=255)
  item_sprice = models.TextField(max_length=50)
  item_image = models.ImageField(upload_to='images/')