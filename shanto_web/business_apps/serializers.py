# serializers.py
from rest_framework import serializers
from .models import *

class ItemCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        fields = ['id', 'category_name']

class ItemBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemBrand
        fields = ['id', 'brand_name']

class ItemUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemUnit
        fields = ['id', 'unit_name']

class ItemProductSerializer(serializers.ModelSerializer):
    category_name = ItemCategorySerializer()
    brand_name = ItemBrandSerializer()
    item_unit = ItemUnitSerializer()

    class Meta:
        model = ItemProduct
        fields = '__all__'#['id', 'item_name', 'category_name', 'brand_name', 'item_model']
        
class MyModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemProduct
        fields = '__all__'