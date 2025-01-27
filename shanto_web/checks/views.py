from django.shortcuts import render, redirect
from .forms import SalesItemForm
from .models import SalesItem, Product

# Create your views here.

def add_sales_item(request):
    if request.method == 'POST':
        form = SalesItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sales_list')  # Assuming you have a view to list sales items
    else:
        form = SalesItemForm()

    return render(request, 'add_sales_item.html', {'form': form})

def search_products(request):
    if request.is_ajax():
        query = request.GET.get('term', '')
        products = Product.objects.filter(name__icontains=query)
        results = []
        for product in products:
            product_json = {}
            product_json['id'] = product.id
            product_json['label'] = product.name
            product_json['value'] = product.name
            results.append(product_json)
        data = json.dumps(results)
    else:
        data = 'fail'
    return HttpResponse(data, 'application/json')
