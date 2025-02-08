import django_filters
from django.forms.widgets import TextInput
from django.forms.widgets import Select
from .models import *

class PurchaseOrderFilter(django_filters.FilterSet):
    porder_status = django_filters.ChoiceFilter(
        field_name='porder_status',
        choices=OrderChoice,
        empty_label='All Orders...'
    )
    class Meta:
        model = PurchaseOrder
        fields = ['porder_status']  # Add the fields you want to filter b