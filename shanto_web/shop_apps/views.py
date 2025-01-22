from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout 
from django.contrib import messages
#from .models import *
from business_apps.models import *
#from shop_apps.forms import *
def view_one(request): 
    data_one = ItemProduct.objects.all() 
    return data_one 
def view_two(request): 
    data_two = ItemCategory.objects.all()
    return data_two
# Create your views here.
def homes(request):
        prod = ItemProduct.objects.all()
        return render(request, "shop_apps/home.html", {'prod': prod})

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
       # prod = ItemProduct.objects.all()
        prod = view_one(request) 
        cat = view_two(request) 
        context = { 
            'prod': prod, 
            'cat': cat, 
            'count': ItemProduct.objects.count(),
        }  
        return render(request, "shop_apps/home.html", {'context': context})

def login_user(request):
    return render(request, "shop_apps/login.html", {})
def logout_user(request):
    logout(request)
    messages.success(request,"Logout Success!")
    return redirect('shop_apps:home')


# Product Item ...
def product(request):  
  prod = ItemProduct.objects.all() 
  return render(request, 'shop_apps/product.html', {'prod': prod})
def product_details(request, pk):  
  prod = get_object_or_404(ItemProduct, pk=pk)
  return render(request, 'shop_apps/product_details.html', {'prod': prod})
