from django.urls import path
from .views import received_items_view

urlpatterns = [
    path('received-items/', received_items_view, name='received_items_view'),
]
# Compare this snippet from shanto_web/service_receiver_digital/views.py:
# from django.shortcuts import render   