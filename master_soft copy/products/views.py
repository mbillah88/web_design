from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from products.models import *
from accounts.models import *
from datetime import datetime
from accounts.context_processors import has_permission
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from django.urls import get_resolver
from django.conf import settings
import json
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
from django.db.models import Q, F, Sum, Count, Max
from django.db import transaction
from decimal import Decimal, ROUND_HALF_UP
from django.utils.timezone import now
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import traceback
from django.db.models import Prefetch


# Product.......
@login_required
def product_list(request):
    current_url = request.resolver_match.view_name if request.resolver_match else None
    if not has_permission(request, current_url, 'access'):
        return JsonResponse({'success': False, 'error': 'অনুমতি নেই'})

    products = Product.objects.select_related('brand', 'category', 'unit', 'warranty').order_by('-created_at')
    
     # ✅ Preprocess low_stock flag
    for product in products:
        try:
            stock = float(product.stock or 0)
            alert = float(product.stock_alert or 0)
            product.low_stock = stock < alert
        except Exception:
            product.low_stock = False  # fallback safety

    categories = Category.objects.order_by('name')
    units = Unit.objects.order_by('name')
    brands = Brand.objects.filter(is_active=True).order_by('name')
    warranties = Warranty.objects.filter(is_active=True).order_by('name')

    return render(request, 'products/product_list.html', {
        'page_title': 'Product List',
        'products': products,
        'categories': categories,
        'units': units,
        'brands': brands,
        'warranties': warranties,
        'can_add': has_permission(request, current_url, 'create'),
        'can_edit': has_permission(request, current_url, 'edit'),
        'can_delete': has_permission(request, current_url, 'delete'),
    })
@login_required
def product_list_json(request):
    products = Product.objects.filter(is_active=True).order_by('name')
    data = [{
        'id': p.id,
        'name': p.name,
        'model': p.model,
        'brand': p.brand.name,
        'category': p.category.name if p.category else '',
        'sale_price': str(p.sale_price),
        'stock_quantity': p.stock_quantity,
    } for p in products]
    return JsonResponse({'success': True, 'data': data})
@csrf_exempt
@login_required
def create_product(request):
    if not has_permission(request, 'products:product_list', 'create'):
        return JsonResponse({'success': False, 'error': 'অনুমতি নেই'}, status=403)

    name = request.POST.get('name', '').strip()
    model = request.POST.get('model', '').strip()
    barcode = request.POST.get('barcode', '').strip()
    image = request.FILES.get('image')

    if not name or not model:
        return JsonResponse({'success': False, 'error': 'নাম ও মডেল আবশ্যক।'})

    if barcode and Product.objects.filter(barcode=barcode).exists():
        return JsonResponse({'success': False, 'error': 'এই বারকোড ইতিমধ্যে আছে।'})

    try:
        product = Product.objects.create(
            name=name,
            model=model,
            barcode=barcode or None,
            image=image,
            description=request.POST.get('description'),
            brand_id=request.POST.get('brand'),
            category_id=request.POST.get('category'),
            unit_id=request.POST.get('unit'),
            warranty_id=request.POST.get('warranty'),
            stock_alert=request.POST.get('stock_alert') or 0,
            purchase_price=request.POST.get('purchase_price') or 0,
            sale_price=request.POST.get('sale_price') or 0,
            discount_price=request.POST.get('discount_price') or None,
            vat_percent=request.POST.get('vat_percent') or 0,
            is_serialized=request.POST.get('is_serialized') == 'true',
            requires_batch=request.POST.get('requires_batch') == 'true',
            is_returnable=request.POST.get('is_returnable') == 'true',
            is_serviceable=request.POST.get('is_serviceable') == 'true',
            warranty_duration_months=request.POST.get('warranty_duration_months') or 0,
            service_interval_days=request.POST.get('service_interval_days') or 0,
            is_active=request.POST.get('is_active') == 'true',
            created_by=request.user
        )
        return JsonResponse({'success': True, 'message': '✅ পণ্য সফলভাবে যোগ হয়েছে।'})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JsonResponse({'success': False, 'error': '⚠️ ডাটাবেজ ত্রুটি: ' + str(e)}, status=500)

@csrf_exempt
@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'})

    barcode = request.POST.get('barcode', '').strip()
    image = request.FILES.get('image')  # ✅

    if Product.objects.exclude(pk=product_id).filter(barcode=barcode).exists():
        return JsonResponse({'success': False, 'error': 'এই বারকোড ইতিমধ্যে আছে।'})

    try:
        product.name = request.POST.get('name')
        product.model = request.POST.get('model')
        product.description = request.POST.get('description')
        product.brand_id = request.POST.get('brand')
        product.category_id = request.POST.get('category')
        product.unit_id = request.POST.get('unit')
        product.warranty_id = request.POST.get('warranty')
        product.barcode = barcode
        product.purchase_price = request.POST.get('purchase_price') or 0
        product.sale_price = request.POST.get('sale_price') or 0
        product.discount_price = request.POST.get('discount_price') or None
        product.vat_percent = request.POST.get('vat_percent') or 0
        product.stock_alert = request.POST.get('stock_alert') or 0
        product.is_serialized = request.POST.get('is_serialized') == 'true'
        product.requires_batch = request.POST.get('requires_batch') == 'true'
        product.is_returnable = request.POST.get('is_returnable') == 'true'
        product.is_serviceable = request.POST.get('is_serviceable') == 'true'
        product.warranty_duration_months = request.POST.get('warranty_duration_months') or 0
        product.service_interval_days = request.POST.get('service_interval_days') or 0
        product.is_active = request.POST.get('is_active') == 'true'
        product.updated_by = request.user

        if image:
            product.image = image  # ✅

        product.save()
        return JsonResponse({'success': True, 'message': '✅ পণ্য আপডেট হয়েছে।'})
    except Exception:
        return JsonResponse({'success': False, 'error': 'ডেটাবেস ত্রুটি।'})
@login_required
def product_json(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return JsonResponse({
        'success': True,
        'product': {
            'id': product.id,
            'name': product.name,
            'model': product.model,
            'description': product.description,
            'brand': product.brand_id,
            'category': product.category_id,
            "image": product.image.url if product.image else "",  
            'unit': product.unit_id,
            'warranty': product.warranty_id,
            'barcode': product.barcode,
            'stock_alert': product.stock_alert,
            'purchase_price': product.purchase_price,
            'sale_price': product.sale_price,
            'discount_price': product.discount_price,
            'vat_percent': product.vat_percent,
            'warranty_duration_months': product.warranty_duration_months,
            'service_interval_days': product.service_interval_days,
            'is_active': product.is_active,
            'is_serialized': product.is_serialized,
            'requires_batch': product.requires_batch,
            'is_returnable': product.is_returnable,
            'is_serviceable': product.is_serviceable,
        }
    })
@csrf_exempt
@login_required
def delete_product(request, product_id):
    current_url = request.resolver_match.view_name
    if not has_permission(request, current_url, 'delete'):
        return JsonResponse({'success': False, 'error': 'অনুমতি নেই'})

    try:
        Product.objects.get(pk=product_id).delete()
        return JsonResponse({'success': True, 'message': '🗑️ পণ্য ডিলিট হয়েছে।'})
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'পণ্য পাওয়া যায়নি।'})
@login_required
def check_barcode(request):
    barcode = request.GET.get('barcode', '').strip()
    if not barcode:
        return JsonResponse({'valid': False, 'error': 'বারকোড আবশ্যক'}, status=400)

    exists = Product.objects.filter(barcode__iexact=barcode).exists()
    return JsonResponse({'valid': not exists})
from .models import Product

@login_required
def product_search(request):
    query = request.GET.get("q", "").strip()
    products = Product.objects.select_related("warranty").all()

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(model__icontains=query) |
            Q(barcode__icontains=query)
        )

    results = []
    for p in products[:20]:
        results.append({
            "id": p.id,
            "text": f"{p.name} ({p.model or 'N/A'}) - ৳{p.purchase_price}",
            "name": p.name,
            "model": p.model,
            "barcode": p.barcode,
            "purchase_price": float(p.purchase_price),
            "is_serialized": p.is_serialized,
            "warranty": p.warranty.name if p.warranty else ""
        })

    return JsonResponse({"products": results})
# Category.......
@login_required
def category_list(request):
    current_url = request.resolver_match.view_name if request.resolver_match else None    
    if not has_permission(request, current_url, 'access'):
        return JsonResponse({'success': False, 'error': 'অনুমতি নেই'})

    categories = Category.objects.all().order_by('name')
    return render(request, 'products/category_list.html', {
        'page_title': 'Category List',
        'categories': categories,
        'can_add': has_permission(request, 'products:category_list', 'create'),
        'can_edit': has_permission(request, 'products:category_list', 'edit'),
        'can_delete': has_permission(request, 'products:category_list', 'delete'),
    })

@csrf_exempt
@login_required
def create_category(request):
    if not has_permission(request, 'products:category_list', 'create'):
        return JsonResponse({'success': False, 'error': 'অনুমতি নেই'}, status=403)

    name = request.POST.get('name', '').strip()
    parent_id = request.POST.get('parent')
    description = request.POST.get('description', '').strip()
    is_active = request.POST.get('is_active') == 'true'
    icon = request.FILES.get('icon')
    banner = request.FILES.get('banner')

    if not name:
        return JsonResponse({'success': False, 'error': 'নাম আবশ্যক'}, status=400)

    if Category.objects.filter(name__iexact=name, parent_id=parent_id or None).exists():
        return JsonResponse({'success': False, 'error': f"'{name}' ইতিমধ্যে আছে"}, status=409)

    try:
        category = Category.objects.create(
            name=name,
            parent_id=parent_id or None,
            description=description,
            is_active=is_active,
            icon=icon,
            banner=banner,
            created_by=request.user
        )
        return JsonResponse({'success': True, 'message': f"✅ '{category.name}' যোগ হয়েছে"})
    except IntegrityError:
        return JsonResponse({'success': False, 'error': 'ডাটাবেস ত্রুটি'}, status=500)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
@csrf_exempt
@login_required
def edit_category(request, pk):
    if not has_permission(request, 'products:category_list', 'edit'):
        return JsonResponse({'success': False, 'error': 'অনুমতি নেই'}, status=403)

    category = get_object_or_404(Category, pk=pk)

    name = request.POST.get('name', '').strip()
    parent_id = request.POST.get('parent')
    description = request.POST.get('description', '').strip()
    is_active = request.POST.get('is_active') == 'true'
    icon = request.FILES.get('icon')
    banner = request.FILES.get('banner')

    if not name:
        return JsonResponse({'success': False, 'error': 'নাম আবশ্যক'}, status=400)

    if Category.objects.filter(name__iexact=name, parent_id=parent_id or None).exclude(pk=pk).exists():
        return JsonResponse({'success': False, 'error': f"'{name}' ইতিমধ্যে আছে"}, status=409)

    try:
        category.name = name
        category.parent_id = parent_id or None
        category.description = description
        category.is_active = is_active
        category.updated_by = request.user

        if icon:
            category.icon = icon
        if banner:
            category.banner = banner

        category.save()
        return JsonResponse({'success': True, 'message': f"✏️ '{category.name}' আপডেট হয়েছে"})
    except IntegrityError:
        return JsonResponse({'success': False, 'error': 'ডাটাবেস ত্রুটি'}, status=500)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@login_required
def delete_category(request, pk):
    current_url = request.resolver_match.view_name if request.resolver_match else None
    if not has_permission(request, current_url, 'delete'):
        return JsonResponse({'success': False, 'error': 'অনুমতি নেই'})

    category = Category.objects.filter(pk=pk).first()
    if not category:
        return JsonResponse({'success': False, 'error': 'ক্যাটাগরি পাওয়া যায়নি'}, status=404)

    name = category.name
    category.delete()
    return JsonResponse({'success': True, 'message': f"🗑️ '{name}' মুছে ফেলা হয়েছে"})
@login_required
def category_json(request, category_id):
    try:
        cat = Category.objects.get(pk=category_id)
        return JsonResponse({
            'success': True,
            'category': {
                'id': cat.id,
                'name': cat.name,
                'parent_id': cat.parent.id if cat.parent else None,
                'description': cat.description,
                'is_active': cat.is_active,
                'icon_url': cat.icon.url if cat.icon else "",
                'banner_url': cat.banner.url if cat.banner else ""
            }
        })
    except Category.DoesNotExist:
        return JsonResponse({'success': False, 'error': '❌ ক্যাটাগরি পাওয়া যায়নি'})

# ✅ Brand List View
@login_required
def brand_list(request):
    current_url = request.resolver_match.view_name if request.resolver_match else None
    if not has_permission(request, current_url, 'access'):
        return JsonResponse({'success': False, 'error': 'অনুমতি নেই'})

    brands = Brand.objects.all().order_by('name')
    return render(request, 'products/brand_list.html', {
        'page_title': 'Brand List',
        'brands': brands,
        'can_add': has_permission(request, 'products:brand_list', 'create'),
        'can_edit': has_permission(request, 'products:brand_list', 'edit'),
        'can_delete': has_permission(request, 'products:brand_list', 'delete'),
    })
@csrf_exempt
@login_required
def create_brand(request):
    if not has_permission(request, 'products:brand_list', 'create'):
        return JsonResponse({'success': False, 'error': 'অনুমতি নেই'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)

    name = request.POST.get('name', '').strip()
    if not name:
        return JsonResponse({'success': False, 'error': 'নাম আবশ্যক।'})

    if Brand.objects.filter(name=name).exists():
        return JsonResponse({'success': False, 'error': 'এই নাম ইতিমধ্যে আছে।'})

    try:
        brand = Brand(
            name=name,
            country=request.POST.get('country', '').strip(),
            support_contact=request.POST.get('support_contact', '').strip(),
            is_active=request.POST.get('is_active') == 'true',
            created_by=request.user
        )
        if request.FILES.get('logo'):
            brand.logo = request.FILES['logo']
        brand.save()
        return JsonResponse({'success': True, 'message': '✅ ব্র্যান্ড যোগ হয়েছে।'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'ডেটাবেস ত্রুটি: {str(e)}'})

@csrf_exempt
@login_required
def edit_brand(request, brand_id):
    if not has_permission(request, 'products:brand_list', 'edit'):
        return JsonResponse({'success': False, 'error': 'অনুমতি নেই'}, status=403)

    brand = get_object_or_404(Brand, pk=brand_id)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)

    name = request.POST.get('name', '').strip()
    if not name:
        return JsonResponse({'success': False, 'error': 'নাম আবশ্যক।'})

    if Brand.objects.exclude(pk=brand_id).filter(name=name).exists():
        return JsonResponse({'success': False, 'error': 'এই নাম ইতিমধ্যে আছে।'})

    try:
        brand.name = name
        brand.country = request.POST.get('country', '').strip()
        brand.support_contact = request.POST.get('support_contact', '').strip()
        brand.is_active = request.POST.get('is_active') == 'true'
        brand.updated_by = request.user

        if request.FILES.get('logo'):
            brand.logo = request.FILES['logo']

        brand.save()
        return JsonResponse({'success': True, 'message': '✅ ব্র্যান্ড আপডেট হয়েছে।'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'ডেটাবেস ত্রুটি: {str(e)}'})

@csrf_exempt
@login_required
def delete_brand(request, brand_id):
    if not has_permission(request, 'products:brand_list', 'delete'):
        return JsonResponse({'success': False, 'error': 'অনুমতি নেই'}, status=403)

    try:
        brand = Brand.objects.get(pk=brand_id)
        brand.delete()
        return JsonResponse({'success': True, 'message': '🗑️ ব্র্যান্ড ডিলিট হয়েছে।'})
    except Brand.DoesNotExist:
        return JsonResponse({'success': False, 'error': '❌ ব্র্যান্ড পাওয়া যায়নি।'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'ডিলিট ত্রুটি: {str(e)}'})

# ✅ AJAX List View
@login_required
def brand_list_json(request, brand_id):
    brand = get_object_or_404(Brand, pk=brand_id)
    return JsonResponse({
        'success': True,
        'brand': {
            'id': brand.id,
            'name': brand.name,
            'country': brand.country,
            'support_contact': brand.support_contact,
            'is_active': brand.is_active,
            'logo_url': brand.logo.url if brand.logo else None
        }
    })


# ✅ Unit List View
@login_required
def unit_list(request):
    if not has_permission(request, 'products:unit_list', 'access'):
        return JsonResponse({'success': False, 'error': 'অনুমতি নেই'})

    units = Unit.objects.all().order_by('name')
    return render(request, 'products/unit_list.html', {
        'page_title': 'ইউনিট তালিকা',
        'units': units,
        'can_add': has_permission(request, 'products:unit_list', 'create'),
        'can_edit': has_permission(request, 'products:unit_list', 'edit'),
        'can_delete': has_permission(request, 'products:unit_list', 'delete'),
    })
@login_required
def unit_json(request, unit_id):
    if not has_permission(request, 'products:unit_list', 'edit'):
        return JsonResponse({'success': False, 'error': 'অনুমতি নেই'}, status=403)

    unit = get_object_or_404(Unit, pk=unit_id)
    return JsonResponse({
        'success': True,
        'unit': {
            'id': unit.id,
            'name': unit.name,
            'symbol': unit.symbol,
            'conversion_factor': float(unit.conversion_factor),
            'is_active': unit.is_active
        }
    })

# ✅ Create Unit
@csrf_exempt
@login_required
def create_unit(request):
    if not has_permission(request, 'products:unit_list', 'create'):
        return JsonResponse({'success': False, 'error': 'অনুমতি নেই'}, status=403)

    name = request.POST.get('name', '').strip()
    symbol = request.POST.get('symbol', '').strip()
    conversion_factor = request.POST.get('conversion_factor') or "1.0000"
    is_active = request.POST.get('is_active') == 'true'

    if not name:
        return JsonResponse({'success': False, 'error': 'নাম আবশ্যক'}, status=400)

    if Unit.objects.filter(name__iexact=name).exists():
        return JsonResponse({'success': False, 'error': f"'{name}' ইতিমধ্যে আছে"}, status=409)

    try:
        unit = Unit.objects.create(
            name=name,
            symbol=symbol,
            conversion_factor=conversion_factor,
            is_active=is_active,
            created_by=request.user
        )
        return JsonResponse({
            'success': True,
            'message': f"✅ '{unit.name}' যোগ হয়েছে",
            'unit': {
                'id': unit.id,
                'name': unit.name,
                'symbol': unit.symbol,
                'conversion_factor': float(unit.conversion_factor),
                'is_active': unit.is_active
            }
        })
    except IntegrityError:
        return JsonResponse({'success': False, 'error': 'ডাটাবেস ত্রুটি'}, status=500)

@csrf_exempt
@login_required
def edit_unit(request, unit_id):
    if not has_permission(request, 'products:unit_list', 'edit'):
        return JsonResponse({'success': False, 'error': 'অনুমতি নেই'}, status=403)

    unit = get_object_or_404(Unit, pk=unit_id)

    name = request.POST.get('name', '').strip()
    symbol = request.POST.get('symbol', '').strip()
    conversion_factor = request.POST.get('conversion_factor') or "1.0000"
    is_active = request.POST.get('is_active') == 'true'

    if not name:
        return JsonResponse({'success': False, 'error': 'নাম আবশ্যক'}, status=400)

    if Unit.objects.exclude(pk=unit_id).filter(name__iexact=name).exists():
        return JsonResponse({'success': False, 'error': f"নাম '{name}' ইতিমধ্যে আছে"}, status=409)

    if symbol and Unit.objects.exclude(pk=unit_id).filter(symbol__iexact=symbol).exists():
        return JsonResponse({'success': False, 'error': f"সিম্বল '{symbol}' ইতিমধ্যে আছে"}, status=409)

    try:
        unit.name = name
        unit.symbol = symbol
        unit.conversion_factor = conversion_factor
        unit.is_active = is_active
        unit.updated_by = request.user
        unit.save()

        return JsonResponse({'success': True, 'message': f"✅ '{unit.name}' সফলভাবে আপডেট হয়েছে"})
    except IntegrityError:
        return JsonResponse({'success': False, 'error': 'ডাটাবেস ত্রুটি'}, status=500)

# ✅ Delete Unit
@csrf_exempt
@login_required
def delete_unit(request, unit_id):
    if not has_permission(request, 'products:unit_list', 'delete'):
        return JsonResponse({'success': False, 'error': 'অনুমতি নেই'}, status=403)

    unit = Unit.objects.filter(pk=unit_id).first()
    if not unit:
        return JsonResponse({'success': False, 'error': 'ইউনিট পাওয়া যায়নি'}, status=404)

    name = unit.name
    unit.delete()
    return JsonResponse({'success': True, 'message': f"🗑️ '{name}' মুছে ফেলা হয়েছে"})

# ✅ AJAX List View
@login_required
def unit_list_json(request):
    if not has_permission(request, 'products:unit_list', 'access'):
        return JsonResponse({'units': [], 'error': 'অনুমতি নেই'}, status=403)

    units = Unit.objects.all().order_by('name')
    data = [{'id': u.id, 'name': u.name} for u in units]
    return JsonResponse({'units': data})

# Warranty.......
@login_required
def warranty_list(request):
    if not has_permission(request, 'products:warranty_list', 'access'):
        return JsonResponse({'success': False, 'error': 'অনুমতি নেই'})
    warranties = Warranty.objects.all().order_by('-updated_at')
    return render(request, 'products/warranty_list.html', {
        'warranties': warranties,
        'can_add': has_permission(request, 'products:warranty_list', 'create'),
        'can_edit': has_permission(request, 'products:warranty_list', 'edit'),
        'can_delete': has_permission(request, 'products:warranty_list', 'delete'),
    })

def warranty_list_json(request):
    warranties = Warranty.objects.filter(is_active=True).order_by('-updated_at')
    data = [{
        'id': w.id,
        'name': w.name,
        'type': w.type,
        'duration_value': w.duration_value,
        'duration_unit': w.duration_unit,
        'is_lifetime': w.is_lifetime,
        'terms': w.terms,
        'is_active': w.is_active
    } for w in warranties]
    return JsonResponse({'success': True, 'warranties': data})

@login_required
def warranty_json(request, warranty_id):
    w = get_object_or_404(Warranty, pk=warranty_id)
    return JsonResponse({
        'success': True,
        'warranty': {
            'id': w.id,
            'name': w.name,
            'type': w.type,
            'duration_value': w.duration_value,
            'duration_unit': w.duration_unit,
            'is_lifetime': w.is_lifetime,
            'terms': w.terms,
            'is_active': w.is_active
        }
    })

@csrf_exempt
@login_required
def create_warranty(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)
    try:
        Warranty.objects.create(
            name=request.POST.get('name'),
            type=request.POST.get('type'),
            duration_value=int(request.POST.get('duration_value')),
            duration_unit=request.POST.get('duration_unit'),
            is_lifetime=request.POST.get('is_lifetime') == 'true',
            terms=request.POST.get('terms', ''),
            is_active=request.POST.get('is_active') == 'true',
            created_by=request.user
        )
        return JsonResponse({'success': True, 'message': '✅ ওয়ারেন্টি যোগ হয়েছে।'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
def edit_warranty(request, warranty_id):
    warranty = get_object_or_404(Warranty, pk=warranty_id)
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)
    try:
        warranty.name = request.POST.get('name')
        warranty.type = request.POST.get('type')
        warranty.duration_value = int(request.POST.get('duration_value'))
        warranty.duration_unit = request.POST.get('duration_unit')
        warranty.is_lifetime = request.POST.get('is_lifetime') == 'true'
        warranty.terms = request.POST.get('terms', '')
        warranty.is_active = request.POST.get('is_active') == 'true'
        warranty.updated_by = request.user
        warranty.save()
        return JsonResponse({'success': True, 'message': '✅ ওয়ারেন্টি আপডেট হয়েছে।'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
def delete_warranty(request, warranty_id):
    try:
        Warranty.objects.get(pk=warranty_id).delete()
        return JsonResponse({'success': True, 'message': '🗑️ ওয়ারেন্টি ডিলিট হয়েছে।'})
    except Warranty.DoesNotExist:
        return JsonResponse({'success': False, 'error': '❌ পাওয়া যায়নি।'})

# 🔹 Create Serial
@csrf_exempt
@login_required
def create_serial(request):
    serial_number = request.POST.get('serial_number', '').strip()
    product_id = request.POST.get('product_id')

    if not serial_number or not product_id:
        return JsonResponse({'success': False, 'error': 'সিরিয়াল এবং পণ্য আবশ্যক।'})

    if ProductSerial.objects.filter(serial_number=serial_number).exists():
        return JsonResponse({'success': False, 'error': 'এই সিরিয়াল ইতিমধ্যে আছে।'})

    try:
        product = Product.objects.get(pk=product_id)
        ProductSerial.objects.create(
            product=product,
            serial_number=serial_number,
            warranty_months=product.warranty_duration_months,
            created_by=request.user
        )
        return JsonResponse({'success': True, 'message': 'সিরিয়াল যোগ হয়েছে।'})
    except Exception:
        return JsonResponse({'success': False, 'error': 'ডেটাবেস ত্রুটি।'}, status=500)

# 🔹 Edit Serial
@csrf_exempt
@login_required
def edit_serial(request, serial_id):
    serial = get_object_or_404(ProductSerial, pk=serial_id)
    serial_number = request.POST.get('serial_number', '').strip()

    if not serial_number:
        return JsonResponse({'success': False, 'error': 'সিরিয়াল আবশ্যক।'})

    if ProductSerial.objects.exclude(pk=serial_id).filter(serial_number=serial_number).exists():
        return JsonResponse({'success': False, 'error': 'এই সিরিয়াল ইতিমধ্যে আছে।'})

    try:
        serial.serial_number = serial_number
        serial.save()
        return JsonResponse({'success': True, 'message': 'সিরিয়াল আপডেট হয়েছে।'})
    except Exception:
        return JsonResponse({'success': False, 'error': 'ডেটাবেস ত্রুটি।'}, status=500)

# 🔹 Delete Serial
@csrf_exempt
@login_required
def delete_serial(request, serial_id):
    try:
        serial = ProductSerial.objects.get(pk=serial_id)
        serial.delete()
        return JsonResponse({'success': True, 'message': 'সিরিয়াল মুছে ফেলা হয়েছে।'})
    except ProductSerial.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'সিরিয়াল পাওয়া যায়নি।'})

# 🔹 List JSON
@login_required
def serial_list_json(request):
    serials = ProductSerial.objects.select_related('product').order_by('-created_at')
    data = [{
        'id': s.id,
        'serial_number': s.serial_number,
        'is_sold': s.is_sold,
        'warranty_expiry': s.warranty_expiry().strftime('%d-%m-%Y') if s.warranty_expiry() else None
    } for s in serials]
    return JsonResponse({'success': True, 'data': data})
# Purchase.......
def calculate_net_total(purchase):
    total = to_decimal(purchase.total)
    discount = to_decimal(purchase.total_discount)

    if purchase.discount_type == "percent":
        discount = (total * discount) / Decimal("100.00")

    net_total = total - discount
    return net_total
@login_required
def purchase_list(request):
    supplier = request.GET.get("supplier", "").strip()
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")
    status = request.GET.get("status")

    # Prefetch purchase items with related product and serials
    item_prefetch = Prefetch(
        'items',
        queryset=PurchaseItem.objects.select_related('product').prefetch_related('serials')
    )

    purchases_qs = (
        Purchase.objects
        .select_related('supplier', 'transaction_type')
        .prefetch_related(item_prefetch)
    )

    # 🔍 Apply filters
    if supplier:
        purchases_qs = purchases_qs.filter(supplier__name__icontains=supplier)

    if from_date:
        try:
            from_dt = datetime.strptime(from_date, "%Y-%m-%d").date()
            purchases_qs = purchases_qs.filter(date__gte=from_dt)
        except ValueError:
            pass

    if to_date:
        try:
            to_dt = datetime.strptime(to_date, "%Y-%m-%d").date()
            purchases_qs = purchases_qs.filter(date__lte=to_dt)
        except ValueError:
            pass

    if status == "paid":
        purchases_qs = purchases_qs.filter(paid__gte=F("total") - F("total_discount"))
    elif status == "due":
        purchases_qs = purchases_qs.filter(paid__lt=F("total") - F("total_discount"))

    purchases_qs = purchases_qs.order_by("-date", "-id")

    # 🔄 Flattened context for table rendering
    purchases = []
    total = paid = due = 0

    for p in purchases_qs:
        total_val = float(p.total or 0)
        paid_val = float(p.paid or 0)
        discount_val = float(p.total_discount or 0)
        due_val = max(total_val - discount_val - paid_val, 0)

        purchases.append({
            "id": p.id,
            "invoice_no": p.invoice_no,
            "supplier": p.supplier.name if p.supplier else "❌",
            "date": p.date,
            "total": total_val,
            "total_discount": discount_val,
            "net_total": total_val - discount_val,
            "paid": paid_val,
            "due": due_val,
            "reference": p.reference or "—",
            "transaction_type": p.transaction_type.name if p.transaction_type else "—",
        })

        total += total_val
        paid += paid_val
        due += due_val

    context = {
        "purchases": purchases,
        "total_summary": {
            "count": len(purchases),
            "total": total,
            "paid": paid,
            "due": due
        },
        "suppliers": Supplier.objects.filter(is_active=True).order_by('name'),
        "products": Product.objects.filter(is_active=True).order_by('name'),
        "methods": PaymentMethod.objects.filter(is_active=True).order_by('name'),
        "transaction_types": TransactionType.objects.filter(module="purchase", is_active=True).order_by('name'),
    }

    return render(request, "products/purchase_list.html", context)
@csrf_exempt
@login_required
def purchase_create(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid method"}, status=405)

    if not request.user.is_staff and not request.user.has_perm("products.add_purchase"):
        return JsonResponse({"success": False, "message": "You don't have permission to create purchases"}, status=403)

    try:
        with transaction.atomic():
            data = request.POST
            serial_map = json.loads(data.get("serials", "{}"))

            # 🔹 Supplier Validation
            supplier_id = data.get("supplier_id")
            if not supplier_id:
                raise ValueError("Supplier is required")
            supplier = Supplier.objects.filter(id=supplier_id).first()
            if not supplier:
                raise ValueError("Invalid supplier")

            # 🔹 Date Validation
            try:
                date_obj = datetime.strptime(data.get("date"), '%Y-%m-%dT%H:%M')
            except Exception:
                raise ValueError("Invalid date format")

            # 🔹 Discount Logic
            discount_value = float(data.get("total_discount") or 0)
            discount_type = data.get("discount_type") or "amount"
            subtotal = float(data.get("subtotal") or 0)

            total_discount = (subtotal * discount_value / 100) if discount_type == "percent" else discount_value
            grand_total = subtotal - total_discount
            if grand_total < 0:
                raise ValueError("Total discount cannot exceed subtotal")

            # 🔹 Create Purchase
            purchase = Purchase.objects.create(
                supplier=supplier,
                date=date_obj,
                invoice_no=data.get("invoice_no") or None,
                reference=data.get("reference") or "",
                total=subtotal,
                total_discount=total_discount,
                paid=0,
                is_returned=False,
                note=data.get("note", ""),
                created_by=request.user,
                updated_by=request.user,
            )

            # 🔹 Product Validation
            product_ids = [key.split("_")[1] for key in data.keys() if key.startswith("price_")]
            if not product_ids:
                raise ValueError("No products selected")

            validated_products = {}
            for pid in product_ids:
                product = Product.objects.filter(id=pid).first()
                if not product:
                    raise ValueError(f"Invalid product ID: {pid}")
                validated_products[pid] = product

            seen_serials = set()

            for pid, product in validated_products.items():
                price = float(data.get(f"price_{pid}", 0))
                discount = float(data.get(f"discount_{pid}", 0))
                serial_list = serial_map.get(pid, [])

                if product.is_serialized:
                    if len(serial_list) == 0:
                        raise ValueError(f"{product.name} requires serials but none provided.")
                    qty = len(serial_list)

                    # 🔒 Serial Duplication Check
                    for sn in serial_list:
                        sn_clean = sn.strip().upper()
                        if sn_clean in seen_serials:
                            raise IntegrityError(f"Duplicate serial in request: {sn_clean}")
                        if ProductSerial.objects.filter(serial_number=sn_clean).exists():
                            raise IntegrityError(f"Serial already exists: {sn_clean}")
                        seen_serials.add(sn_clean)
                else:
                    qty = int(data.get(f"qty_{pid}", 1))
                    if qty <= 0:
                        raise ValueError(f"{product.name}: quantity must be greater than 0")

                item_subtotal = (price * qty) - discount

                item = PurchaseItem.objects.create(
                    purchase=purchase,
                    product=product,
                    price=price,
                    discount=discount,
                    #subtotal=item_subtotal,
                    qty=qty
                )

                # 🔹 Serial Creation
                for sn in serial_list:
                    serial = ProductSerial.objects.create(
                        product=product,
                        serial_number=sn.strip().upper(),
                        warranty_days=product.warranty.duration_days() if product.warranty else 0,
                        created_by=request.user,
                    )
                    item.serials.add(serial)

                # 🔹 Stock Log
                ProductStockLog.objects.create(
                    product=product,
                    change_type="IN",
                    quantity=qty,
                    reference=f"Purchase {purchase.invoice_no}",
                    created_by=request.user
                )

            return JsonResponse({"success": True})

    except IntegrityError as ie:
        return JsonResponse({"success": False, "message": str(ie)}, status=400)
    except ValueError as ve:
        return JsonResponse({"success": False, "message": str(ve)}, status=400)
    except Exception as e:
        print(traceback.format_exc())
        return JsonResponse({"success": False, "message": "Unexpected error: " + str(e)}, status=500)
@login_required
def purchase_edit(request, pk):
    try:
        purchase = get_object_or_404(Purchase, pk=pk)
        items = purchase.items.select_related("product__warranty").prefetch_related("serials")

        serial_map = {}
        item_data = []

        for item in items:
            pid = str(item.product_id)
            serials = list(item.serials.values_list("serial_number", flat=True))
            if serials:
                serial_map[pid] = serials

            item_data.append({
                "product_id": pid,
                "code": item.product.code,
                "name": item.product.name,
                "qty": "Serial" if item.product.is_serialized else item.qty,
                "price": float(item.price),
                "discount": float(item.discount),
                "subtotal": float(item.total_price),
                "warranty": str(item.product.warranty) if item.product.warranty else "—",
                "is_serialized": item.product.is_serialized
            })

        data = {
            "id": purchase.id,
            "invoice_no": purchase.invoice_no or "",
            "date": purchase.date.strftime("%Y-%m-%dT%H:%M"),
            "reference": purchase.reference or "",
            "total": float(purchase.total),
            "total_discount": float(purchase.total_discount),
            "discount_type": purchase.discount_type or "amount",
            "subtotal": float(purchase.subtotal),
            "supplier_id": purchase.supplier_id,
            "items": item_data,
            "serials": serial_map
        }

        return JsonResponse({"success": True, "purchase": data})

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JsonResponse({"success": False, "message": "❌ পারচেস লোড করতে সমস্যা হয়েছে", "error": str(e)}, status=500)
@require_POST
@login_required
def purchase_update(request, pk):
    if not request.user.is_staff and not request.user.has_perm("products.change_purchase"):
        return JsonResponse({"success": False, "message": "আপনার অনুমতি নেই"}, status=403)

    try:
        with transaction.atomic():
            purchase = get_object_or_404(Purchase, pk=pk)
            data = request.POST
            serial_map = json.loads(data.get("serials", "{}"))

            # 🔹 Supplier
            supplier_id = data.get("supplier_id")
            supplier = Supplier.objects.filter(id=supplier_id).first()
            if not supplier:
                raise ValueError("সাপ্লায়ার সঠিক নয়")

            # 🔹 Date
            try:
                date_obj = datetime.strptime(data.get("date"), "%Y-%m-%dT%H:%M")
            except Exception:
                raise ValueError("তারিখ ফরম্যাট সঠিক নয়")

            # 🔹 Discount
            discount_value = float(data.get("total_discount") or 0)
            discount_type = data.get("discount_type") or "amount"
            subtotal = float(data.get("subtotal") or 0)

            total_discount = (subtotal * discount_value / 100) if discount_type == "percent" else discount_value
            grand_total = subtotal - total_discount
            if grand_total < 0:
                raise ValueError("ডিসকাউন্ট সাবটোটাল থেকে বেশি হতে পারে না")

            # 🔁 Update Purchase
            purchase.supplier = supplier
            purchase.date = date_obj
            purchase.invoice_no = data.get("invoice_no") or purchase.invoice_no
            purchase.reference = data.get("reference") or ""
            purchase.total = subtotal
            purchase.total_discount = total_discount
            purchase.note = data.get("note", "")
            purchase.updated_by = request.user
            purchase.save()

            # 🔁 Clear old items
            purchase.items.all().delete()

            # 🔁 Add new items
            product_ids = [key.split("_")[1] for key in data.keys() if key.startswith("price_")]
            if not product_ids:
                raise ValueError("কোনো প্রোডাক্ট সিলেক্ট করা হয়নি")

            for pid in product_ids:
                product = Product.objects.filter(id=pid).first()
                if not product:
                    raise ValueError(f"Invalid product ID: {pid}")

                price = float(data.get(f"price_{pid}", 0))
                discount = float(data.get(f"discount_{pid}", 0))
                serial_list = serial_map.get(pid, [])

                if product.is_serialized:
                    if len(serial_list) == 0:
                        raise ValueError(f"{product.name} requires serials but none provided.")
                    qty = len(serial_list)
                else:
                    qty = int(data.get(f"qty_{pid}", 1))

                item_subtotal = (price * qty) - discount

                item = PurchaseItem.objects.create(
                    purchase=purchase,
                    product=product,
                    price=price,
                    discount=discount,
                    #subtotal=item_subtotal,
                    qty=qty
                )

                # 🔁 Serial creation
                for sn in serial_list:
                    serial = ProductSerial.objects.filter(serial_number=sn).first()

                    if serial:
                        # 🔍 Check if serial is linked to this purchase
                        if serial.purchase_items.filter(purchase=purchase).exists():
                            # ✅ Already linked — safe reuse
                            item.serials.add(serial)
                        elif serial.purchase_items.exists():
                            # ❌ Linked to another purchase — error
                            raise IntegrityError(f"Serial {sn} already used in another purchase")
                        else:
                            # 🔁 Not linked to any purchase — safe reuse
                            item.serials.add(serial)
                    else:
                        # ✅ Create new serial
                        serial = ProductSerial.objects.create(
                            product=product,
                            serial_number=sn,
                            warranty_days=product.warranty.duration_days() if product.warranty else 0,
                            created_by=request.user,
                        )
                        item.serials.add(serial)




                # 🔁 Stock log
                ProductStockLog.objects.create(
                    product=product,
                    change_type="IN",
                    quantity=qty,
                    reference=f"Purchase {purchase.invoice_no or purchase.id}",
                    created_by=request.user
                )

        return JsonResponse({"success": True})

    except IntegrityError as ie:
        return JsonResponse({"success": False, "message": str(ie)}, status=400)
    except ValueError as ve:
        return JsonResponse({"success": False, "message": str(ve)}, status=400)
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JsonResponse({"success": False, "message": "❌ আপডেট করতে সমস্যা হয়েছে", "error": str(e)}, status=500)
@login_required
def purchase_delete(request, pk):
    try:
        purchase = Purchase.objects.filter(id=pk).first()
        if not purchase:
            return JsonResponse({"success": False, "message": "Purchase not found"}, status=404)

        # Optional: prevent delete if returned or paid
        if purchase.is_returned or purchase.paid > 0:
            return JsonResponse({"success": False, "message": "Cannot delete returned or paid purchase"}, status=400)

        purchase.delete()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)
def purchase_summary(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    content_type_id = ContentType.objects.get_for_model(Purchase).id

    payments = Payment.objects.filter(
        content_type_id=content_type_id,
        object_id=purchase.id
    ).order_by("-created_at").values(
        "id", "amount", "method__name", "note", "date", "created_at", "updated_at"
    )

    items_data = []
    for item in purchase.items.all():
        serial_list = []
        if hasattr(item, "serials"):
            serial_list = [s.serial_number.strip() for s in item.serials.all() if s.serial_number]

        items_data.append({
            "product": item.product.name,
            "qty": item.qty,
            "price": float(item.price),
            "discount": float(item.discount),
            "subtotal": float(item.qty * item.price),
            "serials": serial_list
        })

    return JsonResponse({
        "purchase": {
            "id": purchase.id,
            "invoice_no": purchase.invoice_no,
            "date": purchase.date,
            "supplier": {
                "name": purchase.supplier.name,
                "company_name": purchase.supplier.company_name,
                "mobile": purchase.supplier.mobile
            },
            "reference": purchase.reference,
            "total": float(purchase.total),
            "total_discount": float(purchase.total_discount),
            "net_total": float(purchase.total - purchase.total_discount),
            "paid": float(purchase.paid),
            "due": float(purchase.total - purchase.total_discount - purchase.paid),
            "items": items_data,
            "payments": list(payments),
            "content_type_id": content_type_id
        }
    })
@csrf_exempt
@login_required
def process_refund(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid method"}, status=405)

    try:
        data = request.POST
        purchase_id = data.get("purchase_id")
        product_id = data.get("product_id")
        quantity = int(data.get("quantity", 0))
        reason = data.get("reason", "")

        purchase = Purchase.objects.filter(id=purchase_id).first()
        product = Product.objects.filter(id=product_id).first()

        if not purchase or not product:
            return JsonResponse({"success": False, "message": "Invalid purchase or product"}, status=404)

        # 🔹 Refund Entry
        Return.objects.create(
            type="purchase",
            reference_id=purchase.id,
            product=product,
            quantity=quantity,
            reason=reason,
            date=timezone.now().date()
        )
        # Refund payment if exists
        payment = Payment.objects.filter(type="purchase", reference_id=purchase.id, is_refunded=False).first()
        if payment:
            refund_amount = min(payment.amount, quantity * product.purchase_price)
            payment.refund(refund_amount, reason)

        # 🔹 Stock Log: OUT
        ProductStockLog.objects.create(
            product=product,
            change_type="OUT",
            quantity=quantity,
            reference=f"Refund {purchase.invoice_no}",
            created_by=request.user
        )

        # 🔹 Serialized unlink (optional)
        if product.is_serialized:
            refunded_serials = ProductSerial.objects.filter(
                product=product,
                purchase_items__purchase=purchase,
                is_sold=True
            )[:quantity]

            for serial in refunded_serials:
                serial.is_sold = False
                serial.sold_at = None
                serial.save()
                serial.purchase_items.clear()

        return JsonResponse({"success": True})

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JsonResponse({"success": False, "message": str(e)}, status=500)
@login_required
def refund_list(request):
    refunds = Return.objects.select_related("product").order_by("-date")
    return render(request, "products/refund_list.html", {"refunds": refunds})
@login_required
def refund_reason_stats(request):
    stats = Return.objects.values("reason").annotate(total=Count("id")).order_by("-total")
    return JsonResponse({"data": list(stats)})

# Payment.......
@login_required
def payment_list(request):
    supplier = request.GET.get("supplier", "").strip()
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")
    status = request.GET.get("status")

    # ✅ Always define purchases first
    purchases = Purchase.objects.select_related("supplier")

    # 🔍 Apply filters
    if supplier:
        purchases = purchases.filter(supplier__name__icontains=supplier)

    if from_date:
        try:
            from_dt = datetime.strptime(from_date, "%Y-%m-%d").date()
            purchases = purchases.filter(date__gte=from_dt)
        except:
            pass

    if to_date:
        try:
            to_dt = datetime.strptime(to_date, "%Y-%m-%d").date()
            purchases = purchases.filter(date__lte=to_dt)
        except:
            pass

    if status == "paid":
        purchases = purchases.filter(paid__gte=F("total") - F("total_discount"))
    elif status == "due":
        purchases = purchases.filter(paid__lt=F("total") - F("total_discount"))

    # ✅ Safe ordering
    purchases = purchases.order_by("-date")

    context = {
        "purchases": [
            {
                "id": p.id,
                "invoice_no": p.invoice_no,
                "supplier": p.supplier,
                "date": p.date,
                "total": float(p.total),
                "total_discount": float(p.total_discount),
                "net_total": float(p.total) - float(p.total_discount),
                "paid": float(p.paid),
                "due": max(float(p.total) - float(p.total_discount) - float(p.paid), 0),
                "reference": p.reference,
            }
            for p in purchases
        ]
    }

    return render(request, "products/payment_list.html", context)
@login_required
def payment_method_list(request):
    methods = PaymentMethod.objects.filter(is_active=True).values("id", "name")
    return JsonResponse({"methods": list(methods)})
def to_decimal(value):
    try:
        return Decimal(str(value).strip())
    except:
        return Decimal("0.00")
@csrf_exempt
@login_required
def purchase_payment(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid method"}, status=405)

    try:
        data = request.POST
        reference_id = data.get("object_id")
        content_type_id = data.get("content_type_id")
        payment_type = data.get("type")

        methods = data.getlist("payment_method[]")
        amounts = data.getlist("payment_amount[]")
        notes = data.getlist("payment_note[]")

        if not reference_id or not content_type_id or not payment_type:
            return JsonResponse({"success": False, "message": "Missing object/content/type"}, status=400)

        content_type = ContentType.objects.get(id=content_type_id)
        reference_model = content_type.get_object_for_this_type(id=reference_id)

        total_paid = Decimal("0.00")

        for method_id, amount, note in zip(methods, amounts, notes):
            amt = to_decimal(amount)
            if amt <= 0:
                continue

            method = PaymentMethod.objects.filter(id=method_id, is_active=True).first()
            if not method:
                return JsonResponse({"success": False, "message": f"Invalid method ID: {method_id}"}, status=400)

            Payment.objects.create(
                type=payment_type,
                content_type=content_type,
                object_id=reference_id,
                method=method,
                amount=amt,
                note=note,
                date=timezone.now().date(),
                created_by=request.user
            )
            total_paid += amt

        if payment_type == "purchase":
            current_paid = to_decimal(reference_model.paid)
            net_total = to_decimal(reference_model.total) - to_decimal(reference_model.total_discount)
            new_paid = current_paid + total_paid

            if new_paid > net_total:
                return JsonResponse({
                    "success": False,
                    "message": f"⚠️ Overpayment detected! মোট: ৳{net_total}, আগেই দেওয়া: ৳{current_paid}, দিতে চাইছেন: ৳{total_paid}"
                }, status=400)

            reference_model.paid = new_paid
            reference_model.updated_by = request.user
            reference_model.save()

        return JsonResponse({"success": True})

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)
@require_POST
@login_required
def update_payment(request, pk):
    try:
        payment = get_object_or_404(Payment, pk=pk)
        method_id = request.POST.get("method")
        amount = float(request.POST.get("amount", 0))
        note = request.POST.get("note", "")

        method = PaymentMethod.objects.filter(id=method_id).first()
        if not method:
            return JsonResponse({"success": False, "message": "পেমেন্ট মাধ্যম সঠিক নয়"}, status=400)

        if amount <= 0:
            return JsonResponse({"success": False, "message": "পরিমাণ অবশ্যই ০ এর বেশি হতে হবে"}, status=400)

        payment.method = method
        payment.amount = amount
        payment.note = note
        payment.updated_by = request.user
        payment.updated_at = timezone.now()
        payment.save()

        # ✅ Parent sync
        content_object = payment.content_object
        if payment.type == "purchase" and hasattr(content_object, "paid"):
            all_payments = Payment.objects.filter(
                content_type=ContentType.objects.get_for_model(content_object),
                object_id=content_object.id,
                type="purchase"
            )
            content_object.paid = sum(p.amount for p in all_payments)
            content_object.updated_by = request.user
            content_object.save()

        return JsonResponse({"success": True})

    except Exception as e:
        import traceback
        print("❌ Update Error:", traceback.format_exc())
        return JsonResponse({"success": False, "message": "❌ আপডেট করতে সমস্যা হয়েছে", "error": str(e)}, status=500)
@require_POST
@login_required
def bulk_create_payment(request):
    try:
        purchase_id = request.POST.get("purchase_id")
        purchase = get_object_or_404(Purchase, pk=purchase_id)

        methods = request.POST.getlist("methods[]")
        amounts = request.POST.getlist("amounts[]")
        notes = request.POST.getlist("notes[]")

        for method_id, amount_str, note in zip(methods, amounts, notes):
            method = PaymentMethod.objects.filter(id=method_id).first()
            amount = float(amount_str or 0)
            if not method or amount <= 0:
                continue

            Payment.objects.create(
                method=method,
                amount=amount,
                note=note,
                date=timezone.now().date(),
                type="purchase",
                content_type=ContentType.objects.get_for_model(purchase),
                object_id=purchase.id,
                created_by=request.user
            )

        # ✅ Sync paid amount
        all_payments = Payment.objects.filter(
            content_type=ContentType.objects.get_for_model(purchase),
            object_id=purchase.id,
            type="purchase"
        )
        purchase.paid = sum(p.amount for p in all_payments)
        purchase.updated_by = request.user
        purchase.save()

        return JsonResponse({"success": True})

    except Exception as e:
        import traceback
        print("❌ Bulk Create Error:", traceback.format_exc())
        return JsonResponse({"success": False, "message": "❌ পেমেন্ট যোগ করতে সমস্যা হয়েছে"}, status=500)

@csrf_exempt
@login_required
def delete_payment(request, pk):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid method"}, status=405)

    try:
        payment = get_object_or_404(Payment, pk=pk)
        content_object = payment.content_object  # GenericFK

        payment.delete()

        if payment.type == "purchase":
            all_payments = Payment.objects.filter(
                content_type=ContentType.objects.get_for_model(content_object),
                object_id=content_object.id,
                type="purchase"
            )
            total_paid = sum(p.amount for p in all_payments)
            content_object.paid = total_paid
            content_object.updated_by = request.user
            content_object.save()

        return JsonResponse({"success": True, "message": "✅ পেমেন্ট ডিলিট হয়েছে"})

    except Exception as e:
        print("❌ Delete Error:", traceback.format_exc())  # ✅ Full traceback
        return JsonResponse({"success": False, "message": f"❌ {str(e)}"}, status=500)

@require_POST
def create_refund(request, payment_id):
    try:
        payment = Payment.objects.get(id=payment_id)
        amount = Decimal(request.POST.get("amount", "0"))
        reason = request.POST.get("reason", "").strip()

        total_refunded = sum(r.amount for r in payment.refunds.all())
        if amount <= 0 or (total_refunded + amount) > payment.amount:
            return JsonResponse({"success": False, "message": "Invalid refund amount"})

        Refund.objects.create(
            payment=payment,
            amount=amount,
            reason=reason,
            created_by=request.user
        )

        return JsonResponse({"success": True, "message": "Refund processed"})
    except Payment.DoesNotExist:
        return JsonResponse({"success": False, "message": "Payment not found"})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})
# Supplier.......
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)

    return JsonResponse({
        "id": supplier.id,
        "name": supplier.name,
        "company_name": supplier.company_name or "",
        "mobile": supplier.mobile or "",
        "email": supplier.email or "",
        "address": supplier.address or "",
        "district": supplier.district or "",
        "trade_license": supplier.trade_license or "",
        "contact_person": supplier.contact_person or "",
        "contact_mobile": supplier.contact_mobile or "",
        "bank_account": supplier.bank_account or "",
        "payment_terms": supplier.payment_terms or "",
        "is_active": supplier.is_active,
        "created_by": supplier.created_by.username if supplier.created_by else "",
        "updated_by": supplier.updated_by.username if supplier.updated_by else "",
        "created_at": supplier.created_at.strftime("%Y-%m-%d %H:%M"),
        "updated_at": supplier.updated_at.strftime("%Y-%m-%d %H:%M")
    })
@login_required
def create_supplier_ajax(request):
    if request.method == "POST":
        name = request.POST.get("name")
        mobile = request.POST.get("mobile")
        if not name or not mobile:
            return JsonResponse({"success": False, "error": "নাম ও মোবাইল প্রয়োজন"})

        supplier = Supplier.objects.create(
            name=name,
            company_name=request.POST.get("company_name", ""),
            mobile=mobile,
            email=request.POST.get("email", ""),
            address=request.POST.get("address", ""),
            created_by=request.user
        )
        return JsonResponse({
            "success": True,
            "message": f"✅ {supplier.name} যুক্ত হয়েছে",
            "supplier": {
                "id": supplier.id,
                "text": f"{supplier.name} ({supplier.company_name or 'N/A'}) - {supplier.mobile or 'N/A'}"
            }
        })
    return JsonResponse({"success": False, "error": "Invalid request"})
@login_required
def supplier_search(request):
    query = request.GET.get("q", "").strip()
    suppliers = Supplier.objects.all()

    if query:
        suppliers = suppliers.filter(
            Q(name__icontains=query) |
            Q(mobile__icontains=query) |
            Q(company_name__icontains=query)
        )

    results = [
        {
            "id": s.id,
            "text": f"{s.name} ({s.company_name or 'N/A'}) - {s.mobile or 'N/A'}",
            "name": s.name,
            "company_name": s.company_name or "",
            "mobile": s.mobile or "",
            "address": s.address or ""
        }
        for s in suppliers[:20]
    ]
    return JsonResponse({"results": results})
@login_required
def supplier_refund_ledger(request, supplier_id):
    refunds = Return.objects.filter(
        type="purchase",
        product__purchaseitem__purchase__supplier_id=supplier_id
    ).select_related("product").order_by("-date")

    return render(request, "suppliers/refund_ledger.html", {"refunds": refunds})

# Stock In
@csrf_exempt
@login_required
def stock_in(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid method"}, status=405)

    try:
        data = request.POST
        product_id = data.get("product_id")
        qty = int(data.get("qty", 0))
        reference = data.get("reference", "")

        product = Product.objects.filter(id=product_id).first()
        if not product:
            return JsonResponse({"success": False, "message": "Product not found"}, status=404)

        ProductStockLog.objects.create(
            product=product,
            change_type="IN",
            quantity=qty,
            reference=reference,
            created_by=request.user
        )

        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


# Update Supplier Ledger
@csrf_exempt
@login_required
def update_ledger(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid method"}, status=405)

    try:
        data = request.POST
        supplier_id = data.get("supplier_id")
        amount = float(data.get("amount", 0))
        note = data.get("note", "")

        supplier = Supplier.objects.filter(id=supplier_id).first()
        if not supplier:
            return JsonResponse({"success": False, "message": "Supplier not found"}, status=404)

        SupplierLedger.objects.create(
            supplier=supplier,
            amount=amount,
            note=note,
            date=timezone.now().date(),
            created_by=request.user
        )

        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)
