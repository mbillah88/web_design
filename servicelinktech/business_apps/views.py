from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.template import loader

# Create your views here.

def public_home(request):
  template = loader.get_template('public_home.html')
  return HttpResponse(template.render())

def ulogin(request):
  try:
    if request.user.is_authenticated:
      return redirect('business_apps/master.html')

      if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user_obj = User.objects.filter(username = username)
        if not user_obj.exists ():
          messages.info(request, 'Account not found!')
          return HttpResponseRedirect(request.META.get('HTTP_REFFERE'))

          user_obj = authenticate(username = username, password = password)

          if user_obj and user_obj.is_superuser:
            login(request, user_obj)
            return redirect('business_apps/master.html') 

          messages.info(request, 'Invalid Password!')
          return redirect('/')
          template = loader.get_template('business_apps/login.html')
          return HttpResponse(template.render()) 
  except Exception as e:
    print(e)

def sidebar(request):
  template = loader.get_template('business_apps/base.html')
  return HttpResponse(template.render())

def business(request):
  template = loader.get_template('business_apps/new.html')
  return HttpResponse(template.render())

# @login_required