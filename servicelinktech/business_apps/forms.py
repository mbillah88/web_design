# forms.py
from django import forms
from .models import *


class ItemCategoryForm(forms.ModelForm):
    class Meta:
        model = ItemCategory
        fields = "__all__"
      
class ItemBrandForm(forms.ModelForm):
    class Meta:
        model = ItemBrand
        fields = "__all__"
      
class ItemProductForm(forms.ModelForm):
    class Meta:
        model = ItemProduct
        fields = [  'item_name', 
                    'item_model', 
                    'item_description', 
                    'item_sprice', 
                    'item_pprice', 
                    'item_image',
                    'category_name', 
                    'brand_name'
                    #'created_at'
                    ]
      