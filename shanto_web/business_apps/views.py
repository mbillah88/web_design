from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.forms import modelformset_factory
from .forms import *
from. models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
import json
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator
from .filters import *
from .function import get_order_item_count 

# Create your views here.
@login_required
def public_home(request):  
  template = loader.get_template('public_home.html')
  return HttpResponse(template.render())

@login_required
def dashboard(request):
  user = User.objects.all().values() 
  context = {
    'user': user,
    'count': ItemProduct.objects.count(),
  }
  return render(request, 'business_apps/dashboard.html', context)
  
# Product Item ...
@login_required
def product(request):  
  prod = ItemProduct.objects.all() 
  return render(request, 'business_apps/product.html', {'prod': prod})
def product_details(request, pk):  
  prod = get_object_or_404(ItemProduct, pk=pk)
  return render(request, 'business_apps/product_details.html', {'prod': prod})
def product_add(request):
    if request.method == 'POST': 
        form = ItemProductForm(request.POST, request.FILES) 
        if form.is_valid(): 
            form.save() 
            return redirect('slt:product')
    else: 
        messages.success(request, 'Form submission Error')
        form = ItemProductForm() 
    return render(request, 'business_apps/product_add.html', {'form': form})
def product_update(request, pk):
    cat = get_object_or_404(ItemProduct, id=pk)
    if request.method == 'POST': 
        form = ItemProductForm(request.POST, request.FILES, instance=cat) 
        if form.is_valid(): 
            form.save() 
            return redirect('slt:product')          
    else: 
        form = ItemProductForm(instance=cat) 
    return render(request, 'business_apps/product_add.html', {'form': form})
  
# Category ...
@login_required
def category(request):  
  cat = ItemCategory.objects.all() 
  return render(request, 'business_apps/category.html', {'cat': cat})
@login_required
def category_details(request, pk):  
  cat = get_object_or_404(ItemCategory, pk=pk)
  return render(request, 'business_apps/category_details.html', {'cat': cat})
def category_add(request):
    if request.method == 'POST':
        form = ItemCategoryForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect('slt:category')
    else:
        form = ItemCategoryForm()
    return render(request, 'business_apps/category_add.html', {'form': form})
def category_update(request, pk):
    cat = get_object_or_404(ItemCategory, id=pk)
    if request.method == "POST":
        form = ItemCategoryForm(request.POST, request.FILES, instance=cat)
        if form.is_valid():
            form.save()
            return redirect('slt:category')
    else:
        form = ItemCategoryForm(instance=cat)
    return render(request, 'business_apps/category_add.html', {'form': form})

# Brands ....
def brands(request):
  brand = ItemBrand.objects.all() 
  return render(request, 'business_apps/brands.html', {'brand': brand})
def new_brand(request):
    if request.method == 'POST':
        form = ItemBrandForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        return redirect('slt:brands')
    else:
        form = ItemBrandForm()
        return render(request, 'business_apps/brands_new.html', {'form': form})
def brand_update(request, pk):
    brand = get_object_or_404(ItemBrand, id=pk)
    if request.method == 'POST':
        form = ItemBrandForm(request.POST, request.FILES, instance=brand)
        if form.is_valid():
            form.save()
            return redirect('slt:brands')
        else:
            messages.error(request,'username or password not correct')
           # return redirect('slt:new_brand')

    else:
        form = ItemBrandForm(instance=brand)
    return render(request, 'business_apps/brands_new.html', {'form': form})

# Clients ....
def clients(request):
  client = Clients.objects.all() 
  return render(request, 'business_apps/clients.html', {'client': client})
def clients_new(request):
    if request.method == 'POST':
        form = ClientsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        return redirect('slt:clients')
    else:
        form = ClientsForm()
        return render(request, 'business_apps/clients_new.html', {'form': form})
def clients_update(request, pk):
    brand = get_object_or_404(Clients, id=pk)
    if request.method == 'POST':
        form = ClientsForm(request.POST, request.FILES, instance=brand)
        if form.is_valid():
            form.save()
            return redirect('slt:clients')
        else:
            messages.error(request,'Not Update')
           # return redirect('slt:new_brand')

    else:
        form = ClientsForm(instance=brand)
    return render(request, 'business_apps/clients_new.html', {'form': form})

# Supplier ....
def supplier(request):
  supplier = Supplier.objects.all() 
  return render(request, 'business_apps/supplier.html', {'supplier': supplier})
def supplier_new(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('slt:supplier')
    else:
        form = SupplierForm()
        return render(request, 'business_apps/supplier_new.html', {'form': form})
def add_supplier_new(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('slt:purchase_new')
        else:
            form = SupplierForm()
            return render(request, 'business_apps/supplier_new_instance.html', {'form': form})

    else:
        form = SupplierForm()
    return render(request, 'business_apps/supplier_new_instance.html', {'form': form})
def supplier_update(request, pk):
    sup = get_object_or_404(Supplier, id=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, request.FILES, instance=sup)
        if form.is_valid():
            form.save()
            return redirect('slt:supplier')
        else:
            messages.error(request,'Not Update')
            return redirect('slt:new_brand')

    else:
        form = SupplierForm(instance=sup)
    return render(request, 'business_apps/supplier_new.html', {'form': form})

# Sales ....
@login_required
def sales(request):
  return render(request, 'business_apps/sales.html')
def sales_new(request):
  return render(request, 'business_apps/sales_new.html')
def sales_update(request):
  return render(request, 'business_apps/sales_new.html')



# Purchase ....
@login_required
def purchase(request):
    #porder = PurchaseOrder.objects.all().order_by('-porder_create_time')
    products = PurchaseOrderItem.objects.all()
    orders = get_order_item_count().order_by('-porder_create_time')
    # Get the queryset and apply filtering
    filterset = PurchaseOrderFilter(request.GET, queryset=orders)
    filtered_queryset = filterset.qs
    # Set up pagination
    paginator = Paginator(filtered_queryset, 10)  # Show 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'business_apps/purchase.html', {
        #'porder' : porder,
        'products' : products,
        'filterset': filterset,
        'page_obj': page_obj,
        'orders': orders,
    })
def purchase_new(request):
    CartItemFormSet = modelformset_factory(PurchaseOrderItem, form=PurchaseOrderItemForm, extra=0)
    products = ItemProduct.objects.all() 
    if request.method == 'POST':
        customer_form = PurchaseOrderForm(request.POST)
        formset = CartItemFormSet(request.POST,queryset=PurchaseOrderItem.objects.none())        
        #for Data Check...
        for name in request.POST:
            print("{}: {}".format(name, request.POST.getlist(name)))        
        # Print formset errors for debugging
        if not formset.is_valid():
            print("Formset Errors:", formset.errors)
    
        if customer_form.is_valid() and formset.is_valid():
            order = customer_form.save(commit=False)
            order.porder_create_by = request.user
            order.save()
            cart_items = formset.save(commit=False)
            for item in cart_items:
                item.porder_id = order
                item.save()
            return redirect('slt:purchase')  # Redirect to a success page or another view

    else:
        customer_form = PurchaseOrderForm()
        formset = CartItemFormSet(queryset=PurchaseOrderItem.objects.none())

    return render(request, 'business_apps/purchase_new.html', {'form' : customer_form,
            'formset' : formset,
            'products' : products})

def purchase_update(request, pk):
    po = get_object_or_404(PurchaseOrder, id=pk)
    CartItemFormSet = modelformset_factory(PurchaseOrderItem, form=PurchaseOrderItemForm, extra=0)
    products = ItemProduct.objects.all() 
    if request.method == 'POST':
        customer_form = PurchaseOrderForm(request.POST, instance=po)
        formset = CartItemFormSet(request.POST,queryset=PurchaseOrderItem.objects.none())        
        #for Data Check...
        for name in request.POST:
            print("{}: {}".format(name, request.POST.getlist(name)))        
        # Print formset errors for debugging
        if not formset.is_valid():
            print("Formset Errors:", formset.errors)
    
        if customer_form.is_valid() and formset.is_valid():
            order = customer_form.save(commit=False)
            order.porder_create_by = request.user
            order.save()
            cart_items = formset.save(commit=False)
            for item in cart_items:
                item.porder_id = order
                item.save()
            return redirect('slt:purchase')  # Redirect to a success page or another view

    else:
        customer_form = PurchaseOrderForm(instance=po)
        formset = CartItemFormSet(queryset=pk)

    return render(request, 'business_apps/purchase_update.html', {'form' : customer_form,
            'formset' : formset,
            'products' : products})

def purchase_order_process(request):    
    CartItemFormSet = modelformset_factory(PurchaseOrderItem, form=PurchaseOrderItemForm, extra=0)
    products = ItemProduct.objects.all()   

    if request.method == 'POST':
        order_form = PurchaseOrderForm(request.POST)
        formset = CartItemFormSet(request.POST)
        #for Data Check...
        for name in request.POST:
            print("{}: {}".format(name, request.POST.getlist(name)))
        
        # Print formset errors for debugging
        if not formset.is_valid():
            print("Formset Errors:", formset.errors)
    
        if order_form.is_valid and formset.is_valid: 
            order = order_form.save(commit=False)
            order.porder_create_by = request.user
            order.save()
            cart_items = formset.save(commit=False)
            for item in cart_items:
                item.porder_id = '1'
                item.save()   
        return redirect('slt:success')  # Redirect to a success page or another view

    else:
        order_form = PurchaseOrderForm()
        formset = CartItemFormSet(queryset=PurchaseOrderItem.objects.none())

    return render(request, 'business_apps/purchase_new_order.html', {'order_form': order_form, 'formset': formset,'products': products})

# Tools_Unit_View...
@login_required
def settings(request):
    return render(request, 'business_apps/settings.html', {})

@login_required
def tools_unit(request):
    if request.method == 'POST':
        form = ItemUnitForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('slt:tools_unit')
    else:
        form = ItemUnitForm()
    forms = ItemUnit.objects.all().values()
    context = {
        'form' : form,
        'forms' : forms,
    }
    return render(request, 'business_apps/tools_unit.html', context)

@login_required
def tools_unit_update(request, pk):
    unit = get_object_or_404(ItemUnit, id=pk)
    if request.method == 'POST':
        form = ItemUnitForm(request.POST, instance=unit)
        if form.is_valid():
            form.save()
            return redirect('slt:tools_unit')
    else:
        form = ItemUnitForm(instance=unit)
        forms = ItemUnit.objects.all().values()
        context = {
            'form' : form,
            'forms' : forms,
        }
    return render(request, 'business_apps/tools_unit.html', context)

def success(request):
    return HttpResponse('successfully uploaded')

def product_ajax(request):
    product = ItemProduct.objects.all()
    data = [
        {"id": item.id, 
        "name": item.item_name, 
        "description": item.item_description,
        "description": item.item_description,  
        "price": str(item.item_sprice)} 
        for item in product]
    return JsonResponse(data, safe=False)

def product_search(request,pk):
    product = get_object_or_404(ItemProduct, id=pk)
    #product = ItemProduct.objects.all(pk=id)
    serialized_data = [{'field': item.field} for item in data]
    data = {
        "id": product.id, 
        "brand": product.brand_name, 
        "name": product.item_name, 
        "description": product.item_description,
        "price": str(product.item_sprice)} 
    return JsonResponse(data, safe=False)


def product_search1(request):
    query = request.GET.get('query', '')
    items = ItemProduct.objects.filter(item_name__icontains=query)
    data = {"id": item.id, "name": item.item_name, "description": item.item_description, "price": str(item.item_sprice)}
    return JsonResponse(data, safe=False)

def item_detail(request, pk):
    if request.user.is_authenticated:
        try:
            form = ItemProductForm()
            item = ItemProduct.objects.get(pk=pk)
            form = ItemProductForm(instance=item)
            data = {
                'id': item.id,
                'item_name': item.item_name,
                'category_name': item.category_name,
                'brand_name': item.brand_name,
                'item_model': item.item_model,
                'item_description': item.item_description,
                'itme_unit': item.itme_unit,
                'itme_sku': item.itme_sku,
                'itme_alert_qty': item.itme_alert_qty,
                'itme_barcode': item.itme_barcode,
                'item_sprice': item.item_sprice,
                'item_pprice': item.item_pprice,
                'itme_barcode': item.itme_barcode,
                'item_image': item.item_image,
                'itme_status': item.itme_status,
                'created_at': item.created_at,
            }
            return JsonResponse(data)
        except ItemProduct.DoesNotExist:
            return JsonResponse({'error': 'Itme Not found'}, status=404)
    else:
        return JsonResponse({'is_authenticated': False})

@login_required
def supplier_detail(request, pk):    
    if request.user.is_authenticated:
        try:
            item = Supplier.objects.get(pk=pk)
            data = {
                'address': item.supplier_address,
                'mobile': item.supplier_mobile,
            }
            return JsonResponse(data)
        except Supplier.DoesNotExist:
            return JsonResponse({'error': 'Supplier Not found'}, status=404)
    else:
        return JsonResponse({'is_authenticated': False})

class ItemListView(APIView):
    #product = get_object_or_404(ItemProduct, id=pk)
    def get(self, request, pk):
        item = ItemProduct.objects.get(id=pk)
        serializer = ItemProductSerializer(item)
        return Response(serializer.data)

def save_table_data(request):
    CartItemFormSet = modelformset_factory(PurchaseOrderItem, form=PurchaseOrderItemForm, extra=0)
    
    if request.method == 'POST':
        formset = CartItemFormSet(request.POST)
        
        #for Data Check...
        for name in request.POST:
            print("{}: {}".format(name, request.POST.getlist(name)))
        
        # Print formset errors for debugging
        if not formset.is_valid():
            print("Formset Errors:", formset.errors)
    
        if formset.is_valid():
            formset.save()
            return redirect('slt:purchase')  # Redirect to a success page or another view
    
    else:
        formset = CartItemFormSet(queryset=PurchaseOrderItem.objects.none())
    
    return render(request, 'business_apps/purchase_new_order.html', {'formset': formset})