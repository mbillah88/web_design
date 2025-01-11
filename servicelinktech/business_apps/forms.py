# forms.py
from django import forms
from .models import ItemCategory


class ItemCategoryForm(forms.ModelForm):
    class Meta:
        model = ItemCategory
        fields = ['category_name', 'category_description', 'cat_image']
      