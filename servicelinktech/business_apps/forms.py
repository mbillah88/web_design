# forms.py
from django import forms
from .models import *


class ItemCategoryForm(forms.ModelForm):
    class Meta:
        model = ItemCategory
        fields = "__all__"
        widgets = { 
            'cat_image': forms.ClearableFileInput(attrs={ 'id': 'imageInput' }),       
         }
      
class ItemBrandForm(forms.ModelForm):
    class Meta:
        model = ItemBrand
        fields = "__all__"
        widgets = { 
            'brand_image': forms.ClearableFileInput(attrs={ 'class': 'form-control-file', 'id': 'imageInput' }),
       
         }
      
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
                    'brand_name',
                    'created_at'
                    ]
      
        widgets = { 
            'item_image': forms.ClearableFileInput(attrs={ 'id': 'imageInput' }),   
            'created_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),     
         }


class ClientsForm(forms.ModelForm):
    class Meta:
        model = Clients
        fields = "__all__"


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = "__all__"