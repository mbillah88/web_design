# forms.py
from django import forms
from .models import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

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

        widgets = { 
            'item_image': forms.ClearableFileInput(attrs={ 'id': 'imageInput' }),   
            'created_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),           
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['item_name'].empty_label = "Select Item..."
        self.fields['category_name'].empty_label = "Select Category..."
        self.fields['brand_name'].empty_label = "Select Brand..."
        self.fields['itme_unit'].empty_label = "Select Unit..."

class ClientsForm(forms.ModelForm):
    class Meta:
        model = Clients
        fields = "__all__"

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = "__all__" 

class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['supplier_id','porder_total','porder_discount','porder_status','porder_note']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['supplier_id'].empty_label = "Select Supplier..."

class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ['item_id','itme_qty','item_pprice']

    helper = FormHelper()
    helper.add_input(Submit('submit', 'Submit', css_class='bg-success'))
    helper.form_method = 'POST'

class PurchasePaymentForm(forms.ModelForm):
    class Meta:
        model = PurchasePayment
        fields = "__all__"

# Settings Tools .........
class ItemUnitForm(forms.ModelForm):    
    class Meta:
        model = ItemUnit
        fields = "__all__"


    helper = FormHelper()
    helper.add_input(Submit('submit', 'Submit', css_class='bg-success'))
    helper.form_method = 'POST'
        #min_value=1, max_value=10, initial=1