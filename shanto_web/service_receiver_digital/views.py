from django.shortcuts import render
from .models import ReceivedItem, ReceivedItemSpec

def received_items_view(request):
    received_items = ReceivedItem.objects.all()
    received_item_specs = ReceivedItemSpec.objects.select_related('received_item', 'item_type_specification', 'item_type_specification__item_type', 'item_type_specification__item_specification')

    context = {
        'received_items': received_items,
        'received_item_specs': received_item_specs,
    }

    return render(request, 'service_receiver_digital/received_items.html', context)
