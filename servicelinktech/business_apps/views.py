from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader

# Create your views here.

def public_home(request):
  template = loader.get_template('public_home.html')
  return HttpResponse(template.render())

def ulogin(request):
  template = loader.get_template('business_apps/login.html')
  return HttpResponse(template.render())

def sidebar(request):
  template = loader.get_template('business_apps/base.html')
  return HttpResponse(template.render())

def business(request):
  template = loader.get_template('business_apps/base.html')
  return HttpResponse(template.render())

# @login_required