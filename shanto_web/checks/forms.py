from django import forms
from .models import SalesItem, Product

class SalesItemForm(forms.ModelForm):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), widget=forms.TextInput(attrs={'class': 'searchable'}))

    class Meta:
        model = SalesItem
        fields = ['product', 'quantity']
