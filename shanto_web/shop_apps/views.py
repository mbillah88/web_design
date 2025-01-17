from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout 
from django.contrib import messages
from .models import *
from shop_apps.forms import *
# Create your views here.

def home(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request,"Login Success!")
            return redirect('shop_apps:home')
        else:
            messages.success(request,"Ooooff Login Error!")
            return redirect('shop_apps:login')
    else:
        return render(request, "shop_apps/home.html", {})

def login_user(request):
    return render(request, "shop_apps/login.html", {})
def logout_user(request):
    logout(request)
    messages.success(request,"Logout Success!")
    return redirect('shop_apps:home')


# Product Item ...
@login_required
def product(request):  
  prod = ItemProduct.objects.all() 
  return render(request, 'shop_apps/product.html', {'prod': prod})
def product_details(request, pk):  
  prod = get_object_or_404(ItemProduct, pk=pk)
  return render(request, 'shop_apps/product_details.html', {'prod': prod})
def product_add(request):
    if request.method == 'POST': 
        form = ItemProductForm(request.POST, request.FILES) 
        if form.is_valid(): 
            form.save() 
            return redirect('slt:product')
    else: 
        messages.success(request, 'Form submission Error')
        form = ItemProductForm() 
    return render(request, 'shop_apps/product_add.html', {'form': form})
def product_update(request, pk):
    cat = get_object_or_404(ItemProduct, id=pk)
    if request.method == 'POST': 
        form = ItemProductForm(request.POST, request.FILES, instance=cat) 
        if form.is_valid(): 
            form.save() 
            return redirect('slt:product')          
    else: 
        form = ItemProductForm(instance=cat) 
    return render(request, 'shop_apps/product_add.html', {'form': form})
  
# Category ...
@login_required
def category(request):  
  cat = ItemCategory.objects.all() 
  return render(request, 'shop_apps/category.html', {'cat': cat})
@login_required
def category_details(request, pk):  
  cat = get_object_or_404(ItemCategory, pk=pk)
  return render(request, 'shop_apps/category_details.html', {'cat': cat})
def category_add(request):
    if request.method == 'POST':
        form = ItemCategoryForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect('slt:category')
    else:
        form = ItemCategoryForm()
    return render(request, 'shop_apps/category_add.html', {'form': form})
def category_update(request, pk):
    cat = get_object_or_404(ItemCategory, id=pk)
    if request.method == "POST":
        form = ItemCategoryForm(request.POST, request.FILES, instance=cat)
        if form.is_valid():
            form.save()
            return redirect('slt:category')
    else:
        form = ItemCategoryForm(instance=cat)
    return render(request, 'shop_apps/category_add.html', {'form': form})

# Brands ....
def brands(request):
  brand = ItemBrand.objects.all() 
  return render(request, 'shop_apps/brands.html', {'brand': brand})
def new_brand(request):
    if request.method == 'POST':
        form = ItemBrandForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        return redirect('slt:brands')
    else:
        form = ItemBrandForm()
        return render(request, 'shop_apps/brands_new.html', {'form': form})
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
    return render(request, 'shop_apps/brands_new.html', {'form': form})
