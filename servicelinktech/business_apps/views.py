from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.template import loader
from .forms import ItemCategoryForm
from. models import ItemCategory

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
  
@login_required
def new_sales(request):
  user = User.objects.all().values() 
  context = {
    'user': user,
  }
  return render(request, 'business_apps/new_sales.html', context)

def sales(request):
    return HttpResponse('sales_list successfully uploaded')

def item(request):
  template = loader.get_template('business_apps/item.html')
  return HttpResponse(template.render())

def item_add(request):
  template = loader.get_template('business_apps/item_add.html')
  return HttpResponse(template.render())


@login_required
def category(request):  
  cat = ItemCategory.objects.all() 
  return render(request, 'business_apps/item_category.html', {'cat': cat})

@login_required
def category_details(request, pk):  
  cat = get_object_or_404(ItemCategory, pk=pk)
  return render(request, 'business_apps/item_category_details.html', {'cat': cat})

def category_add(request):
    if request.method == 'POST':
        form = ItemCategoryForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect('slt:category')
    else:
        form = ItemCategoryForm()
    return render(request, 'business_apps/item_category_add.html', {'form': form})

def category_update(request, pk):
    cat = get_object_or_404(ItemCategory, id=pk)
    if request.method == "POST":
        form = ItemCategoryForm(request.POST, request.FILES, instance=cat)
        if form.is_valid():
            form.save()
            return redirect('slt:category')
    else:
        form = ItemCategoryForm(instance=cat)
    return render(request, 'business_apps/item_category_add.html', {'form': form})
def new_brands(request):
  template = loader.get_template('business_apps/new_brands.html')
  return HttpResponse(template.render())

def brands(request):
  template = loader.get_template('business_apps/brands.html')
  return HttpResponse(template.render())

def success(request):
    return HttpResponse('successfully uploaded')
