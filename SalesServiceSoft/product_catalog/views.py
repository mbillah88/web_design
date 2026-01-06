from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Q
from .models import Product, Unit, Category, Brand
from .forms import ProductForm, UnitForm, CategoryForm, BrandForm

# ─────────────────────────────────────────────
# 📦 Product Views
def product_list(request):
    query = request.GET.get('q', '')
    products = Product.objects.select_related('unit', 'category', 'brand')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(sku__icontains=query) |
            Q(category__name__icontains=query) |
            Q(brand__name__icontains=query)
        )
    products = products.order_by('-created_at')
    return render(request, 'product_catalog/product_list.html', {
        'products': products,
        'query': query
    })

def product_add(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, "✅ নতুন প্রোডাক্ট সফলভাবে যুক্ত হয়েছে।")
        return redirect('product_list')
    elif request.method == 'POST':
        messages.error(request, "❌ প্রোডাক্ট যুক্ত করতে সমস্যা হয়েছে।")
    return render(request, 'product_catalog/product_form.html', {'form': form})

def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if form.is_valid():
        form.save()
        messages.success(request, "✅ প্রোডাক্ট সফলভাবে আপডেট হয়েছে।")
        return redirect('product_list')
    elif request.method == 'POST':
        messages.error(request, "❌ আপডেট করতে সমস্যা হয়েছে।")
    return render(request, 'product_catalog/product_form.html', {'form': form})

@require_POST
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, "🗑️ প্রোডাক্ট সফলভাবে মুছে ফেলা হয়েছে।")
    return redirect('product_list')

# ─────────────────────────────────────────────
# 🧮 Unit Views
def unit_list(request):
    query = request.GET.get('q', '')
    units = Unit.objects.all()
    if query:
        units = units.filter(name__icontains=query)
    return render(request, 'product_catalog/unit_list.html', {
        'units': units,
        'query': query
    })
def unit_add(request):
    form = UnitForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "✅ নতুন ইউনিট সফলভাবে যুক্ত হয়েছে।")
        return redirect('unit_list')
    elif request.method == 'POST':
        messages.error(request, "❌ ইউনিট যুক্ত করতে সমস্যা হয়েছে।")
    return render(request, 'product_catalog/unit_form.html', {'form': form})
def add_unit_ajax(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        symbol = request.POST.get('symbol')
        if name and symbol:
            unit = Unit.objects.create(name=name, symbol=symbol)
            return JsonResponse({
                'success': True,
                'unit_id': unit.id,
                'unit_name': f"{unit.name} ({unit.symbol})"
            })
    return JsonResponse({'success': False})
def unit_edit(request, pk):
    unit = get_object_or_404(Unit, pk=pk)
    form = UnitForm(request.POST or None, instance=unit)
    if form.is_valid():
        form.save()
        messages.success(request, "✅ ইউনিট সফলভাবে আপডেট হয়েছে।")
        return redirect('unit_list')
    elif request.method == 'POST':
        messages.error(request, "❌ আপডেট করতে সমস্যা হয়েছে।")
    return render(request, 'product_catalog/unit_form.html', {'form': form})
@require_POST
def unit_delete(request, pk):
    unit = get_object_or_404(Unit, pk=pk)
    unit.delete()
    messages.success(request, "🗑️ ইউনিট সফলভাবে মুছে ফেলা হয়েছে।")
    return redirect('unit_list')

# ─────────────────────────────────────────────
# 🗂️ Category Views
def category_list(request):
    query = request.GET.get('q', '')
    categories = Category.objects.all()
    if query:
        categories = categories.filter(name__icontains=query)
    return render(request, 'product_catalog/category_list.html', {
        'categories': categories,
        'query': query
    })

def category_add(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "✅ নতুন ক্যাটাগরি সফলভাবে যুক্ত হয়েছে।")
        return redirect('category_list')
    elif request.method == 'POST':
        messages.error(request, "❌ ক্যাটাগরি যুক্ত করতে সমস্যা হয়েছে।")
    return render(request, 'product_catalog/category_form.html', {'form': form})

def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save()
        messages.success(request, "✅ ক্যাটাগরি সফলভাবে আপডেট হয়েছে।")
        return redirect('category_list')
    elif request.method == 'POST':
        messages.error(request, "❌ আপডেট করতে সমস্যা হয়েছে।")
    return render(request, 'product_catalog/category_form.html', {'form': form})

@require_POST
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, "🗑️ ক্যাটাগরি সফলভাবে মুছে ফেলা হয়েছে।")
    return redirect('category_list')

# ─────────────────────────────────────────────
# 🏷️ Brand Views
def brand_list(request):
    query = request.GET.get('q', '')
    brands = Brand.objects.all()
    if query:
        brands = brands.filter(name__icontains=query)
    return render(request, 'product_catalog/brand_list.html', {
        'brands': brands,
        'query': query
    })

def brand_add(request):
    form = BrandForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, "✅ নতুন ব্র্যান্ড সফলভাবে যুক্ত হয়েছে।")
        return redirect('brand_list')
    elif request.method == 'POST':
        messages.error(request, "❌ ব্র্যান্ড যুক্ত করতে সমস্যা হয়েছে।")
    return render(request, 'product_catalog/brand_form.html', {'form': form})

def brand_edit(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    form = BrandForm(request.POST or None, request.FILES or None, instance=brand)
    if form.is_valid():
        form.save()
        messages.success(request, "✅ ব্র্যান্ড সফলভাবে আপডেট হয়েছে।")
        return redirect('brand_list')
    elif request.method == 'POST':
        messages.error(request, "❌ আপডেট করতে সমস্যা হয়েছে।")
    return render(request, 'product_catalog/brand_form.html', {'form': form})

@require_POST
def brand_delete(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    brand.delete()
    messages.success(request, "🗑️ ব্র্যান্ড সফলভাবে মুছে ফেলা হয়েছে।")
    return redirect('brand_list')
