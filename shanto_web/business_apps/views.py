from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse
from django.template import loader
from .forms import *
from. models import *

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
def supplier_update(request, pk):
    sup = get_object_or_404(Supplier, id=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, request.FILES, instance=sup)
        if form.is_valid():
            form.save()
            return redirect('slt:supplier')
        else:
            messages.error(request,'Not Update')
           # return redirect('slt:new_brand')

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
  return render(request, 'business_apps/purchase.html')
def purchase_new(request):
  return render(request, 'business_apps/purchase_new.html')
def purchase_update(request):
  return render(request, 'business_apps/purchase_update.html')
def purchase_order_process(request):    
    if request.method == 'POST':
        if request.user.is_authenticated:
            user = request.user
            #create_order = PurchaseOrder(user = user)
            #create_order.save()
            return render(request, 'business_apps/purchase.html', {'user': user})
def success(request):
    return HttpResponse('successfully uploaded')
