from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.template import loader

# Create your views here.
@login_required
def public_home(request):  
  template = loader.get_template('public_home.html')
  return HttpResponse(template.render())

@login_required
def new_sales(request):
  user = User.objects.all().values() 
  context = {
    'user': user,
  }
  return render(request, 'business_apps/new_sales.html', context)

@login_required
def dashboard(request):
  user = User.objects.all().values() 
  context = {
    'user': user,
  }
  return render(request, 'business_apps/dashboard.html', context)
  
  