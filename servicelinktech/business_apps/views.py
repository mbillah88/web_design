from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

# Create your views here.

def public_home(request):
  template = loader.get_template('public_home.html')
  return HttpResponse(template.render())