from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.forms import modelformset_factory
from .forms import *
from .models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
import json
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator
from .filters import *
from .function import *
from django.db.models import Sum
from django.db.models import Sum, F, Q, Value, Count, ExpressionWrapper, DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone

# Create your views here.
@login_required
def public_home(request):  
  template = loader.get_template('public_home.html')
  return HttpResponse(template.render())

@login_required
def dashboard(request):
    user = User.objects.all().values() 
    orders = get_order_item_count().order_by('-porder_create_time')

    # Get the purchase summary
    purchase_summary = PurchaseOrderItem.objects.values('item_id__id', 'item_id__item_name') \
        .annotate(total_purchased_quantity=Sum('item_qty')) \
        .annotate(total_purchased_amount=Sum('item_pprice')) \
        .order_by('item_id__id')

    # Get the sales summary
    sales_summary = SalesOrderItem.objects.values('item_id__id', 'item_id__item_name') \
        .annotate(total_sold_quantity=Sum('item_qty')) \
        .annotate(total_sold_amount=Sum('item_sprice')) \
        .order_by('item_id__id')

    # Convert purchase_summary and sales_summary to dictionaries for easier processing
    purchase_dict = {item['item_id__id']: item for item in purchase_summary}
    sales_dict = {item['item_id__id']: item for item in sales_summary}

    # Calculate the inventory
    inventory_summary = []
    for item_id, purchase_item in purchase_dict.items():
        item_name = purchase_item['item_id__item_name']
        total_purchased_quantity = purchase_item['total_purchased_quantity']
        total_purchased_amount = purchase_item['total_purchased_amount']

        sales_item = sales_dict.get(item_id, {'total_sold_quantity': 0, 'total_sold_amount': 0})
        total_sold_quantity = sales_item['total_sold_quantity']
        total_sold_amount = sales_item['total_sold_amount']

        remaining_quantity = total_purchased_quantity - total_sold_quantity

        inventory_summary.append({
            'item_id': item_id,
            'item_name': item_name,
            'total_purchased_quantity': total_purchased_quantity,
            'total_purchased_amount': total_purchased_amount,
            'total_sold_quantity': total_sold_quantity,
            'total_sold_amount': total_sold_amount,
            'remaining_quantity': remaining_quantity
        })

    # Optionally, print the inventory summary for verification
    #for item in inventory_summary:
    #    print(item)

        
    # Get the current date
    current_date = timezone.localtime().date()

    # Define an ExpressionWrapper to calculate the total amount for purchases and sales
    purchase_total_amount = ExpressionWrapper(F('item_qty') * F('item_pprice'), output_field=DecimalField())
    sales_total_amount = ExpressionWrapper(F('item_qty') * F('item_sprice'), output_field=DecimalField())

    # Get the purchase summary for the current date
    purchase_summary_today = list(PurchaseOrderItem.objects.filter(porder_id__porder_create_time__date=current_date).values('item_id__id', 'item_id__item_name') \
        .annotate(total_purchased_quantity=Sum('item_qty')) \
        .annotate(total_purchased_amount=Sum(purchase_total_amount)) \
        .annotate(total_orders=Count('porder_id', distinct=True)) \
        .annotate(total_items=Count('item_id')) \
        .order_by('item_id__id'))

    # Get the total orders and total price for purchases
    total_purchase_orders = len(set(item['total_orders'] for item in purchase_summary_today))
    total_purchase_items = sum(item['total_purchased_quantity'] for item in purchase_summary_today)
    total_purchase_amount = sum(item['total_purchased_amount'] for item in purchase_summary_today)

    # Get the sales summary for the current date
    sales_summary_today = list(SalesOrderItem.objects.filter(sorder_id__sorder_create_time__date=current_date).values('item_id__id', 'item_id__item_name') \
        .annotate(total_sold_quantity=Sum('item_qty')) \
        .annotate(total_sold_amount=Sum(sales_total_amount)) \
        .annotate(total_orders=Count('sorder_id', distinct=True)) \
        .annotate(total_items=Count('item_id')) \
        .order_by('item_id__id'))

    # Get the total orders and total price for sales
    total_sales_orders = len(set(item['total_orders'] for item in sales_summary_today))
    total_sales_items = sum(item['total_sold_quantity'] for item in sales_summary_today)
    total_sales_amount = sum(item['total_sold_amount'] for item in sales_summary_today)

    # Print the summaries for verification
    #print("Today's Purchase Summary:")
    #for item in purchase_summary_today:
    #    print(item)

    #print("\nTotal Purchase Orders:", total_purchase_orders)
    #print("Total Purchase Items:", total_purchase_items)
    #print("Total Purchase Amount:", total_purchase_amount)

    #print("\nToday's Sales Summary:")
    #for item in sales_summary_today:
    #    print(item)

    #print("\nTotal Sales Orders:", total_sales_orders)
    #print("Total Sales Items:", total_sales_items)
    #print("Total Sales Amount:", total_sales_amount)

    context = {
        'user': user,
        'orders': orders,
        'purchase_summary': purchase_summary,
        'sales_summary': sales_summary,
        'inventory_summary': inventory_summary,
        'purchase_summary_today': purchase_summary_today,
        'sales_summary_today': sales_summary_today,
        'total_sales_orders': total_sales_orders,
        'total_sales_items': total_sales_items,
        'total_sales_amount': total_sales_amount,
        'total_purchase_orders': total_purchase_orders,
        'total_purchase_items': total_purchase_items,
        'total_purchase_amount': total_purchase_amount,
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
  #porder = PurchaseOrder.objects.all().order_by('-porder_create_time')
    products = SalesOrderItem.objects.all()
    orders = get_sorder_item_count().order_by('-sorder_create_time')
    # Get the queryset and apply filtering
    filterset = SalesOrderFilter(request.GET, queryset=orders)
    filtered_queryset = filterset.qs
    # Set up pagination
    paginator = Paginator(filtered_queryset, 10)  # Show 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'business_apps/sales.html', {
        #'porder' : porder,
        'products' : products,
        'filterset': filterset,
        'page_obj': page_obj,
        'orders': orders,
    })
def sales_new(request):
    CartItemFormSet = modelformset_factory(SalesOrderItem, form=SalesOrderItemForm, extra=0)
    products = ItemProduct.objects.all() 
    if request.method == 'POST':
        customer_form = SalesOrderForm(request.POST)
        payment_form = SalesPaymentForm(request.POST)
        formset = CartItemFormSet(request.POST,queryset=SalesOrderItem.objects.none())        
        #for Data Check...
        for name in request.POST:
            print("{}: {}".format(name, request.POST.getlist(name)))        
        # Print formset errors for debugging
        if not formset.is_valid():
            print("Formset Errors:", formset.errors)
        
        if customer_form.is_valid() and formset.is_valid() and payment_form.is_valid():
            order = customer_form.save(commit=False)
            order.sorder_create_by = request.user
            order.save()
            cart_items = formset.save(commit=False)
            for item in cart_items:
                item.sorder_id = order
                item.save()
            payment = payment_form.save(commit=False)
            payment.sorder_id = order
            payment.payment_create_by = request.user
            payment.save()
            return redirect('slt:sales')  # Redirect to a success page or another view

    else:
        customer_form = SalesOrderForm()
        payment_form = SalesPaymentForm()
        formset = CartItemFormSet(queryset=SalesOrderItem.objects.none())

    return render(request, 'business_apps/sales_new.html', {
        'form' : customer_form,
        'pay_form' : payment_form,
        'formset' : formset,
        'products' : products})            
def sales_update(request, pk):
    sorder_id = get_object_or_404(SalesOrder, id=pk)
    sorder_pay = get_object_or_404(SalesPayment, sorder_id=pk)
    CartItemFormSet = modelformset_factory(SalesOrderItem, form=SalesOrderItemForm, extra=0)
    products = ItemProduct.objects.all() 
    if request.method == 'POST':
        customer_form = SalesOrderForm(request.POST, instance=sorder_id)
        payment_form = SalesPaymentForm(request.POST, instance=sorder_pay)
        formset = CartItemFormSet(request.POST)        
        #for Data Check...
        for name in request.POST:
            print("{}: {}".format(name, request.POST.getlist(name)))        
        # Print formset errors for debugging
        if not formset.is_valid():
            print("Formset Errors:", formset.errors)
        
        if customer_form.is_valid() and formset.is_valid() and payment_form.is_valid():
            order = customer_form.save(commit=False)
            order.sorder_create_by = request.user
            order.save()
            cart_items = formset.save(commit=False)
            for item in cart_items:
                item.sorder_id = order
                item.save()
            payment = payment_form.save(commit=False)
            payment.sorder_id = order
            payment.payment_create_by = request.user
            payment.save()
            return redirect('slt:sales')  # Redirect to a success page or another view

    else:
        customer_form = SalesOrderForm(instance=sorder_id)
        payment_form = SalesPaymentForm(instance=sorder_pay)
        sorder_id = SalesOrderItem.objects.filter(sorder_id_id=pk) 
        formset = CartItemFormSet(queryset=sorder_id)
    return render(request, 'business_apps/sales_update.html', {
        'form' : customer_form,
        'pay_form' : payment_form,
        'formset' : formset,
        'products' : products})      

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
        payment_form = PurchasePaymentForm(request.POST)
        formset = CartItemFormSet(request.POST,queryset=PurchaseOrderItem.objects.none())        
        #for Data Check...
        for name in request.POST:
            print("{}: {}".format(name, request.POST.getlist(name)))        
        # Print formset errors for debugging
        if not formset.is_valid():
            print("Formset Errors:", formset.errors)
    
        if customer_form.is_valid() and formset.is_valid() and payment_form.is_valid():
            order = customer_form.save(commit=False)
            order.porder_create_by = request.user
            order.save()
            cart_items = formset.save(commit=False)
            for item in cart_items:
                item.porder_id = order
                item.save()
            payment = payment_form.save(commit=False)
            payment.order_id = order
            payment.payment_create_by = request.user
            payment.save()
            return redirect('slt:purchase')  # Redirect to a success page or another view

    else:
        customer_form = PurchaseOrderForm()
        payment_form = PurchasePaymentForm()
        formset = CartItemFormSet(queryset=PurchaseOrderItem.objects.none())

    return render(request, 'business_apps/purchase_new.html', {
        'form' : customer_form,
        'pay_form' : payment_form,
        'formset' : formset,
        'products' : products})
def purchase_due_pay(request, pk):
    po = get_object_or_404(PurchaseOrder, id=pk)
    payo = get_object_or_404(PurchasePayment, order_id=pk)
    CartItemFormSet = modelformset_factory(PurchaseOrderItem, form=PurchaseOrderItemForm, extra=0)

    if request.method == 'POST':
        customer_form = PurchaseOrderForm(request.POST, instance=po)
        payment_form = PurchasePaymentForm(request.POST, instance=payo)
        
        if customer_form.is_valid() and payment_form.is_valid():
            order = customer_form.save(commit=False)
            order.porder_create_by = request.user
            order.save()
            payment = payment_form.save(commit=False)
            payment.order_id = order
            payment.payment_create_by = request.user
            payment.save()
            return redirect('slt:purchase')  # Redirect to a success page or another view

    else:
        customer_form = PurchaseOrderForm(instance=po)
        payment_form = PurchasePaymentForm(instance=payo)
        porder = PurchaseOrderItem.objects.filter(porder_id_id=pk) 
        formset = CartItemFormSet(queryset=porder)
        return render(request, 'business_apps/purchase_due_payment.html', {
            'form' : customer_form,
            'pay_form' : payment_form,
            'formset' : formset})
def purchase_update(request, pk):
    po = get_object_or_404(PurchaseOrder, id=pk)
    payo = get_object_or_404(PurchasePayment, order_id=pk)
    CartItemFormSet = modelformset_factory(PurchaseOrderItem, form=PurchaseOrderItemForm, extra=0)
    products = ItemProduct.objects.all() 
    if request.method == 'POST':
        customer_form = PurchaseOrderForm(request.POST, instance=po)
        payment_form = PurchasePaymentForm(request.POST, instance=payo)
        formset = CartItemFormSet(request.POST)        
        #for Data Check...
        for name in request.POST:
            print("{}: {}".format(name, request.POST.getlist(name)))        
        # Print formset errors for debugging
        if not formset.is_valid():
            print("Formset Errors:", formset.errors)
    
        if customer_form.is_valid() and formset.is_valid() and payment_form.is_valid():
            order = customer_form.save(commit=False)
            order.porder_create_by = request.user
            order.save()
            cart_items = formset.save(commit=False)
            for item in cart_items:
                item.porder_id = order
                item.save()
            payment = payment_form.save(commit=False)
            payment.order_id = order
            payment.payment_create_by = request.user
            payment.save()
            return redirect('slt:purchase')  # Redirect to a success page or another view

    else:
        customer_form = PurchaseOrderForm(instance=po)
        payment_form = PurchasePaymentForm(instance=payo)
        porder = PurchaseOrderItem.objects.filter(porder_id_id=pk) 
        formset = CartItemFormSet(queryset=porder)
        return render(request, 'business_apps/purchase_update.html', {
            'form' : customer_form,
            'pay_form' : payment_form,
            'formset' : formset,
            'products' : products})
def item_delete_row(request, purchase_pk, row_id):
    obj = get_object_or_404(PurchaseOrderItem, id=row_id)
    obj.delete()
    return JsonResponse({'status': 'success', 'message': 'Row deleted successfully'})

#Service.....
def service(request):
    return render(request, 'business_apps/service.html', {})
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
                'item_unit': item.item_unit,
                'item_sku': item.item_sku,
                'iteme_alert_qty': item.item_alert_qty,
                'item_barcode': item.item_barcode,
                'item_sprice': item.item_sprice,
                'item_pprice': item.item_pprice,
                'item_barcode': item.item_barcode,
                'item_image': item.item_image,
                'item_status': item.item_status,
                'created_at': item.created_at,
            }
            return JsonResponse(data)
        except ItemProduct.DoesNotExist:
            return JsonResponse({'error': 'item Not found'}, status=404)
    else:
        return JsonResponse({'is_authenticated': False})

@login_required
def supplier_detail(request, supplier_pk):    
    if request.user.is_authenticated:
        try:
            item = Supplier.objects.get(pk=supplier_pk)
            data = {
                'address': item.supplier_address,
                'mobile': item.supplier_mobile,
            }
            return JsonResponse(data)
        except Supplier.DoesNotExist:
            return JsonResponse({'error': 'Supplier Not found'}, status=404)
    else:
        return JsonResponse({'is_authenticated': False})

@login_required
def supplier_details(request, purchase_pk, supplier_pk):    
    if request.user.is_authenticated:
        try:
            item = Supplier.objects.get(pk=supplier_pk)
            data = {
                'address': item.supplier_address,
                'mobile': item.supplier_mobile,
            }
            return JsonResponse(data)
        except Supplier.DoesNotExist:
            return JsonResponse({'error': 'Supplier Not found'}, status=404)
    else:
        return JsonResponse({'is_authenticated': False})

@login_required
def customer_details(request, customer_pk):    
    if request.user.is_authenticated:
        try:
            item = Clients.objects.get(pk=customer_pk)
            data = {
                'address': item.client_address,
                'mobile': item.client_mobile,
            }
            return JsonResponse(data)
        except Clients.DoesNotExist:
            return JsonResponse({'error': 'Clients Not found'}, status=404)
    else:
        return JsonResponse({'is_authenticated': False})
@login_required
def customer_details_sales(request, sales_pk, customer_pk):    
    if request.user.is_authenticated:
        try:
            item = Clients.objects.get(pk=customer_pk)
            data = {
                'address': item.client_address,
                'mobile': item.client_mobile,
            }
            return JsonResponse(data)
        except Clients.DoesNotExist:
            return JsonResponse({'error': 'Clients Not found'}, status=404)
    else:
        return JsonResponse({'is_authenticated': False})

@login_required
def products_details_sales(request, sales_pk, product_search_pk):    
    if request.user.is_authenticated:
        try:
            item = ItemProduct.objects.get(pk=product_search_pk)
            #data = {
            #    'address': item.supplier_address,
            #    'mobile': item.supplier_mobile,
            #}
            serializer = ItemProductSerializer(item)
            return JsonResponse(serializer.data)
            #return JsonResponse(data)
        except ItemProduct.DoesNotExist:
            return JsonResponse({'error': 'Product Not found'}, status=404)
    else:
        return JsonResponse({'is_authenticated': False})

@login_required
def pproducts_detail(request, product_search_pk):    
    if request.user.is_authenticated:
        try:
            item = ItemProduct.objects.get(pk=product_search_pk)
            #data = {
            #    'address': item.supplier_address,
            #    'mobile': item.supplier_mobile,
            #}
            serializer = ItemProductSerializer(item)
            return JsonResponse(serializer.data)
            #return JsonResponse(data)
        except ItemProduct.DoesNotExist:
            return JsonResponse({'error': 'Product Not found'}, status=404)
    else:
        return JsonResponse({'is_authenticated': False})

@login_required
def pproducts_details(request, purchase_pk, product_search_pk):    
    if request.user.is_authenticated:
        try:
            item = ItemProduct.objects.get(pk=product_search_pk)
            #data = {
            #    'address': item.supplier_address,
            #    'mobile': item.supplier_mobile,
            #}
            serializer = ItemProductSerializer(item)
            return JsonResponse(serializer.data)
            #return JsonResponse(data)
        except ItemProduct.DoesNotExist:
            return JsonResponse({'error': 'Product Not found'}, status=404)
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
# Reports panel...............
@login_required
def reports(request):
    return render(request, 'business_apps/reports.html', {})

def report_summary_daily(request):
    # Get the purchase summary
    purchase_summary = PurchaseOrderItem.objects.values('item_id__id', 'item_id__item_name') \
        .annotate(total_purchased_quantity=Sum('item_qty')) \
        .annotate(total_purchased_amount=Sum('item_pprice')) \
        .order_by('item_id__id')

    # Get the sales summary
    sales_summary = SalesOrderItem.objects.values('item_id__id', 'item_id__item_name') \
        .annotate(total_sold_quantity=Sum('item_qty')) \
        .annotate(total_sold_amount=Sum('item_sprice')) \
        .order_by('item_id__id')

    # Convert purchase_summary and sales_summary to dictionaries for easier processing
    purchase_dict = {item['item_id__id']: item for item in purchase_summary}
    sales_dict = {item['item_id__id']: item for item in sales_summary}

    # Calculate the inventory
    inventory_summary = []
    for item_id, purchase_item in purchase_dict.items():
        item_name = purchase_item['item_id__item_name']
        total_purchased_quantity = purchase_item['total_purchased_quantity']
        total_purchased_amount = purchase_item['total_purchased_amount']

        sales_item = sales_dict.get(item_id, {'total_sold_quantity': 0, 'total_sold_amount': 0})
        total_sold_quantity = sales_item['total_sold_quantity']
        total_sold_amount = sales_item['total_sold_amount']

        remaining_quantity = total_purchased_quantity - total_sold_quantity

        inventory_summary.append({
            'item_id': item_id,
            'item_name': item_name,
            'total_purchased_quantity': total_purchased_quantity,
            'total_purchased_amount': total_purchased_amount,
            'total_sold_quantity': total_sold_quantity,
            'total_sold_amount': total_sold_amount,
            'remaining_quantity': remaining_quantity
        })

    # Optionally, print the inventory summary for verification
    for item in inventory_summary:
        print(item)

        
    # Get the current date
    current_date = timezone.localtime().date()

    # Define an ExpressionWrapper to calculate the total amount for purchases and sales
    purchase_total_amount = ExpressionWrapper(F('item_qty') * F('item_pprice'), output_field=DecimalField())
    sales_total_amount = ExpressionWrapper(F('item_qty') * F('item_sprice'), output_field=DecimalField())

    # Get the purchase summary for the current date
    purchase_summary_today = list(PurchaseOrderItem.objects.filter(porder_id__porder_create_time__date=current_date).values('item_id__id', 'item_id__item_name') \
        .annotate(total_purchased_quantity=Sum('item_qty')) \
        .annotate(total_purchased_amount=Sum(purchase_total_amount)) \
        .annotate(total_orders=Count('porder_id', distinct=True)) \
        .annotate(total_items=Count('item_id')) \
        .order_by('item_id__id'))

    # Get the total orders and total price for purchases
    total_purchase_orders = len(set(item['total_orders'] for item in purchase_summary_today))
    total_purchase_items = sum(item['total_purchased_quantity'] for item in purchase_summary_today)
    total_purchase_amount = sum(item['total_purchased_amount'] for item in purchase_summary_today)

    # Get the sales summary for the current date
    sales_summary_today = list(SalesOrderItem.objects.filter(sorder_id__sorder_create_time__date=current_date).values('item_id__id', 'item_id__item_name') \
        .annotate(total_sold_quantity=Sum('item_qty')) \
        .annotate(total_sold_amount=Sum(sales_total_amount)) \
        .annotate(total_orders=Count('sorder_id', distinct=True)) \
        .annotate(total_items=Count('item_id')) \
        .order_by('item_id__id'))

    # Get the total orders and total price for sales
    total_sales_orders = len(set(item['total_orders'] for item in sales_summary_today))
    total_sales_items = sum(item['total_sold_quantity'] for item in sales_summary_today)
    total_sales_amount = sum(item['total_sold_amount'] for item in sales_summary_today)

    # Print the summaries for verification
    print("Today's Purchase Summary:")
    for item in purchase_summary_today:
        print(item)

    print("\nTotal Purchase Orders:", total_purchase_orders)
    print("Total Purchase Items:", total_purchase_items)
    print("Total Purchase Amount:", total_purchase_amount)

    print("\nToday's Sales Summary:")
    for item in sales_summary_today:
        print(item)

    print("\nTotal Sales Orders:", total_sales_orders)
    print("Total Sales Items:", total_sales_items)
    print("Total Sales Amount:", total_sales_amount)

    context = {
        'purchase_summary': purchase_summary,
        'sales_summary': sales_summary,
        'inventory_summary': inventory_summary,
        'purchase_summary_today': purchase_summary_today,
        'sales_summary_today': sales_summary_today,
        'total_sales_orders': total_sales_orders,
        'total_sales_items': total_sales_items,
        'total_sales_amount': total_sales_amount,
        'total_purchase_orders': total_purchase_orders,
        'total_purchase_items': total_purchase_items,
        'total_purchase_amount': total_purchase_amount,
    }
    return render(request, 'business_apps/reports/daily_reports_summary.html', context)
#Printing page....
def pinvoice(request, pk):
    po = get_object_or_404(PurchaseOrder, id=pk)
    payo = get_object_or_404(PurchasePayment, order_id=pk)
    CartItemFormSet = modelformset_factory(PurchaseOrderItem, form=PurchaseOrderItemForm, extra=0)
    products = ItemProduct.objects.all() 
    customer_form = PurchaseOrderForm(instance=po)
    payment_form = PurchasePaymentForm(instance=payo)
    porder = PurchaseOrderItem.objects.filter(porder_id_id=pk) 
    formset = CartItemFormSet(queryset=porder)
    return render(request, 'business_apps/reports/pinvoice.html', {
        'form' : customer_form,
        'pay_form' : payment_form,
        'formset' : formset,
        'products' : products})

#Printing page....
def sinvoice(request, pk):
    po = get_object_or_404(SalesOrder, id=pk)
    payo = get_object_or_404(SalesPayment, sorder_id_id=pk)
    CartItemFormSet = modelformset_factory(SalesOrderItem, form=SalesOrderItemForm, extra=0)
    customer_form = SalesOrderForm(instance=po)
    payment_form = SalesPaymentForm(instance=payo)
    porder = SalesOrderItem.objects.filter(sorder_id_id=pk) 
    formset = CartItemFormSet(queryset=porder)
    return render(request, 'business_apps/reports/sinvoice.html', {
        'form' : customer_form,
        'pay_form' : payment_form,
        'formset' : formset})