from django.shortcuts import render
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

def category_add(request):

    if request.method == 'POST':
        form = ItemCategoryForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect('success')
    else:
        form = ItemCategoryForm()
    return render(request, 'business_apps/item_category_add.html', {'form': form})

@login_required
def category(request):  
  cat = ItemCategory.objects.all() 
  return render(request, 'business_apps/item_category.html', {'cat': cat})

 # return render(request, 'blog/post_list.html', {'posts': posts})
 # template = loader.get_template('business_apps/item_category.html')
  #return HttpResponse(template.render())

def new_brands(request):
  template = loader.get_template('business_apps/new_brands.html')
  return HttpResponse(template.render())

def brands(request):
  template = loader.get_template('business_apps/brands.html')
  return HttpResponse(template.render())

def success(request):
    return HttpResponse('successfully uploaded')
