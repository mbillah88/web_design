# serializers.py
from rest_framework import serializers
from .models import *

class MyModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'