# forms.py
from django import forms
from .models import *

# iterable 
PaymentChoice =( 
    ("1", "Cash"), 
    ("2", "Card"), 
    ("3", "Others"), 
    ("4", "Due"), 
) 
  
# iterable 
OrderChoice =( 
    ("1", "Received"), 
    ("2", "Pending"), 
    ("3", "Ordered"), 
    ("4", "Cancel"), 
) 

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
        fields = "__all__"

        readonly_fields = ('created_at')

        widgets = { 
            'item_image': forms.ClearableFileInput(attrs={ 'id': 'imageInput' }),   
            'created_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),   
            #'itme_unit': forms.ChoiceField(choices = OrderChoice),  
         }

class ClientsForm(forms.ModelForm):
    class Meta:
        model = Clients
        fields = "__all__"

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = "__all__"

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = "__all__"

class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = "__all__"

class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = "__all__"

class PurchasePaymentForm(forms.ModelForm):
    class Meta:
        model = PurchasePayment
        fields = "__all__"

        #min_value=1, max_value=10, initial=1