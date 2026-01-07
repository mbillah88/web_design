# views.py
import os
from django.conf import settings
from pyreportjasper import PyReportJasper
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, DetailView
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from django.http import JsonResponse, FileResponse, HttpResponse
from django.db.models import Q
from django.utils.dateparse import parse_date
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Count # ✅ এই লাইনটি যোগ করো
import json
from django.contrib import messages
from datetime import datetime
from accounts.models import CustomUser
from django.db.models import F, Value, Func, CharField
from django.db.models.functions import Concat
from django.db.models import Sum
from django.db.models import Prefetch
from django.http import HttpResponseBadRequest, HttpResponseServerError

from .models import (
    TestCategory, TestSubCategory, TestGroup, TestItem, TestGroupItem, TestResult, 
    Patient, PatientVisit, IPDAdmission, 
    Bed, Consultant, BedTransferLog, BedChargeEntry, ConsultantChangeLog,
    AdviceInvoice, Payment, PaymentMethod, PaymentMethodType
)
from .forms import (
    TestCategoryForm, TestGroupForm, TestItemForm,
    PatientForm, PatientVisitForm, IPDAdmissionForm
)

# Consultant Views can be added here if needed
def consultant_search(request):
    q = request.GET.get('q', '')
    consultants = Consultant.objects.filter(name__icontains=q)[:20]

    results = [
        {'id': c.id, 'text': f"{c.name} ({c.type})"}
        for c in consultants
    ]
    return JsonResponse({'results': results})

# --- Test Views ---
def test_category_list(request):
    categories = TestCategory.objects.all()
    return render(request, 'diagnostics/test_manage/test_category_list.html', {'categories': categories})

def test_category_create(request):
    form = TestCategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('diagnostics:test_category_list')
    return render(request, 'diagnostics/test_manage/test_category_form.html', {'form': form})

def test_category_edit(request, pk):
    category = get_object_or_404(TestCategory, pk=pk)
    form = TestCategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save()
        return redirect('diagnostics:test_category_list')
    return render(request, 'diagnostics/test_manage/test_category_form.html', {'form': form})

def test_category_delete(request, pk):
    category = get_object_or_404(TestCategory, pk=pk)
    category.delete()
    return redirect('diagnostics:test_category_list')

def test_category_groups(request, pk):
    category = get_object_or_404(TestCategory, pk=pk)
    groups = TestGroup.objects.filter(sub_category__category=category)
    return render(request, 'diagnostics/test_manage/test_group_list.html', {
        'groups': groups,
        'category': category
    })

def get_subcategories(request): 
    category_id = request.GET.get('category_id') 
    if category_id: 
        subcategories = TestSubCategory.objects.filter(category_id=category_id).values('id', 'name') 
        return JsonResponse(list(subcategories), safe=False)
    return JsonResponse([], safe=False)
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from .models import TestGroup, TestCategory, TestSubCategory, TestGroupItem

def test_group_manager(request):
    raw_category_id = request.GET.get('category_id')
    raw_subcategory_id = request.GET.get('subcategory_id')
    search_query = request.GET.get('q', '').strip()
    raw_group_id = request.GET.get('group_id')

    category_id = int(raw_category_id) if raw_category_id and raw_category_id.isdigit() else None
    subcategory_id = int(raw_subcategory_id) if raw_subcategory_id and raw_subcategory_id.isdigit() else None
    group_id = int(raw_group_id) if raw_group_id and raw_group_id.isdigit() else None

    categories = TestCategory.objects.all()
    subcategories = TestSubCategory.objects.select_related('category').all()

    groups = TestGroup.objects.select_related('sub_category__category').annotate(
        item_count=Count('group_items')
    )

    if category_id:
        groups = groups.filter(sub_category__category_id=category_id)

    if subcategory_id:
        groups = groups.filter(sub_category_id=subcategory_id)

    if search_query:
        groups = groups.filter(name__icontains=search_query)

    sort_by = request.GET.get('sort', 'name')
    if sort_by in ['name', '-name', 'price', '-price', 'item_count', '-item_count']:
        groups = groups.order_by(sort_by)

    per_page_options = [10, 25, 50, 100]
    per_page = request.GET.get('per_page')
    try:
        per_page = int(per_page)
        if per_page not in per_page_options:
            per_page = 10
    except (TypeError, ValueError):
        per_page = 10

    paginator = Paginator(groups, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    selected_group = None
    items = []
    if group_id:
        selected_group = get_object_or_404(TestGroup, id=group_id)
        items = selected_group.group_items.select_related('item').all()

    context = {
        'categories': categories,
        'subcategories': subcategories,
        'groups': groups,
        'selected_group_id': group_id,
        'selected_group': selected_group,
        'items': items,
        'selected_category_id': str(category_id) if category_id else '',
        'selected_subcategory_id': str(subcategory_id) if subcategory_id else '',
        'search_query': search_query,
        'page_obj': page_obj,
        'sort_by': sort_by,
        'per_page_options': per_page_options,
        'per_page': per_page,
    }
    return render(request, 'diagnostics/test_manage/test_group_list.html', context)

def test_group_form(request, pk=None):
    edit_mode = pk is not None
    group = get_object_or_404(TestGroup, pk=pk) if edit_mode else None

    categories = TestCategory.objects.all()
    subcategories = TestSubCategory.objects.select_related('category').all()
    subcategories_json = json.dumps([
        {'id': sub.id, 'name': sub.name, 'category_id': sub.category.id}
        for sub in subcategories
    ])

    if request.method == 'POST':
        form = TestGroupForm(request.POST, instance=group)
        if form.is_valid():
            group = form.save(commit=False)
            if not edit_mode:
                group.created_by = request.user
            group.update_by = request.user
            group.save()

            # Clear old group_items if editing
            if edit_mode:
                group.group_items.all().delete()

            # Save selected items via TestGroupItem
            item_ids = request.POST.getlist('item_id[]')
            orders = request.POST.getlist('item_order[]')
            actives = request.POST.getlist('item_active[]')

            for i, item_id in enumerate(item_ids):
                if item_id:
                    item = get_object_or_404(TestItem, id=item_id)
                    TestGroupItem.objects.create(
                        group=group,
                        item=item,
                        order=int(orders[i]) if i < len(orders) else 0
                    )
                    # Optional: update item.is_active if needed
                    if str(i) in actives:
                        item.is_active = True
                    else:
                        item.is_active = False
                    item.save()

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'group_id': group.id})

            return redirect('diagnostics:test_group_list')

        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    else:
        form = TestGroupForm(instance=group)

    return render(request, 'diagnostics/test_manage/test_group_form.html', {
        'form': form,
        'group': group or {},
        'items': group.group_items.select_related('item') if group else [],
        'all_items': TestItem.objects.order_by('name'),
        'categories': categories,
        'subcategories': subcategories,
        'subcategories_json': subcategories_json,
        'edit_mode': edit_mode,
        'success': False,
    })

 
def test_group_form00(request, pk=None):
    edit_mode = pk is not None
    group = get_object_or_404(TestGroup, pk=pk) if edit_mode else None

    categories = TestCategory.objects.all()
    subcategories = TestSubCategory.objects.select_related('category').all()
    subcategories_json = json.dumps([
        {'id': sub.id, 'name': sub.name, 'category_id': sub.category.id}
        for sub in subcategories
    ])

    if request.method == 'POST':
        form = TestGroupForm(request.POST, instance=group)
        if form.is_valid():
            group = form.save(commit=False)
            if not edit_mode:
                group.created_by = request.user
            group.update_by = request.user
            group.save()

            # Clear old items if editing
            if edit_mode:
                group.items.all().delete()

            # Save new items
            names = request.POST.getlist('item_name[]')
            units = request.POST.getlist('item_unit[]')
            unit2s = request.POST.getlist('item_unit2[]')
            refs = request.POST.getlist('item_reference[]')
            actives = request.POST.getlist('item_active[]')

            for i, name in enumerate(names):
                if name.strip():
                    TestItem.objects.create(
                        group=group,
                        name=name.strip(),
                        unit=units[i].strip(),
                        unit2=unit2s[i].strip() if i < len(unit2s) else '',
                        reference_range=refs[i].strip(),
                        is_active=str(i) in actives,
                        created_by=request.user,
                        updated_by=request.user
                    )

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'group_id': group.id})

            return redirect('diagnostics:test_group_list')

        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    else:
        form = TestGroupForm(instance=group)

    return render(request, 'diagnostics/test_manage/test_group_form.html', {
        'form': form,
        'group': group or {},
        'items': group.items.all() if group else [],
        'categories': categories,
        'subcategories': subcategories,
        'subcategories_json': subcategories_json,
        'edit_mode': edit_mode,
        'success': False,
    })
    
def test_group_list(request):
    groups = TestGroup.objects.all()
    return render(request, 'diagnostics/test_manage/test_group_list.html', {'groups': groups})

def test_group_create(request): 
    categories = TestCategory.objects.all() 
    subcategories = TestSubCategory.objects.select_related('category').all() 
    subcategories_json = json.dumps([ 
        {'id': sub.id, 'name': sub.name, 'category_id': sub.category.id} 
        for sub in subcategories 
    ]) 
    if request.method == 'POST': 
        form = TestGroupForm(request.POST) 
        if form.is_valid(): 
            group = form.save(commit=False) 
            group.created_by = request.user 
            group.update_by = request.user 
            group.save() 
            return render(request, 'diagnostics/test_manage/test_group_form.html', { 
                'form': form, 
                'group': group, 
                'items': [], 
                'categories': categories, 
                'subcategories': subcategories, 
                'subcategories_json': subcategories_json, 
                'edit_mode': False, 
                'success': True, 
            }) 
    else:
        form = TestGroupForm()
    return render(request, 'diagnostics/test_manage/test_group_form.html', {
        'form': form,
        'group': {},
        'items': [],
        'categories': categories,
        'subcategories': subcategories,
        'subcategories_json': subcategories_json,
        'edit_mode': False,
        'success': False,
    })
def test_group_edit(request, pk):
    group = get_object_or_404(TestGroup, pk=pk)
    categories = TestCategory.objects.all()
    subcategories = TestSubCategory.objects.select_related('category').all()
    subcategories_json = json.dumps([
        {'id': sub.id, 'name': sub.name, 'category_id': sub.category.id}
        for sub in subcategories
    ])

    if request.method == 'POST':
        form = TestGroupForm(request.POST, instance=group)
        if form.is_valid():
            group = form.save(commit=False)
            group.update_by = request.user
            group.save()
            items = group.items.all()
            return render(request, 'diagnostics/test_manage/test_group_form.html', {
                'form': form,
                'group': group,
                'items': items,
                'categories': categories,
                'subcategories': subcategories,
                'subcategories_json': subcategories_json,
                'edit_mode': True,
                'success': True,
            })
        else:
            items = group.items.all()  # fallback
    else:
        form = TestGroupForm(instance=group)
        items = group.items.all()

    return render(request, 'diagnostics/test_manage/test_group_form.html', {
        'form': form,
        'group': group,
        'items': items,
        'categories': categories,
        'subcategories': subcategories,
        'subcategories_json': subcategories_json,
        'edit_mode': True,
        'success': False,
    })

def test_item_list(request):
    items = TestItem.objects.select_related('group').order_by('group__name', 'name')
    return render(request, 'diagnostics/test_manage/test_item_list.html', {
        'items': items,
        'title': '🧬 All Test Items'
    })

def test_item_create(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = TestItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.updated_by = request.user
            item.save()
            return JsonResponse({
                'success': True,
                'item': {
                    'id': item.id,
                    'name': item.name,
                    'unit': item.unit,
                    'reference_range': item.reference_range,
                }
            })
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

def patient_report_list(request):
    query = request.GET.get('q', '').strip()
    visits = PatientVisit.objects.select_related('patient').order_by('-visit_date')

    if query:
        visits = visits.filter(
            Q(patient__name__icontains=query) |
            Q(patient__phone__icontains=query) |
            Q(id__icontains=query)
        )

    return render(request, 'diagnostics/test_manage/report_patient_list.html', {
        'visits': visits,
        'query': query,
    })
    
def patient_report_detail(request, visit_id):
    visit = get_object_or_404(
        PatientVisit.objects.select_related('patient', 'consultant'),
        id=visit_id
    )

    results = TestResult.objects.filter(visit=visit).select_related(
        'test_item', 'advice_entry__group'
    ).order_by('advice_entry__group__name', 'test_item__name')

    if request.method == 'POST':
        for result in results:
            edited_value = request.POST.get(f'result_{result.id}')
            edited_unit = request.POST.get(f'unit_{result.id}')
            if edited_value:
                result.edited_result = edited_value
                result.edited_unit = edited_unit
                result.edited_by = request.user
                result.edited_at = timezone.now()
                result.save()
        messages.success(request, "✅ রেজাল্ট সফলভাবে সংরক্ষণ করা হয়েছে।")
        return redirect('diagnostics:patient_report_detail', visit_id=visit.id)

    return render(request, 'diagnostics/test_manage/report_detail.html', {
        'visit': visit,
        'results': results,
    })

# --- Patient Views ---
class PatientListView(ListView):
    model = Patient
    template_name = 'diagnostics/patients/patient_list.html'
    context_object_name = 'patients'

class PatientCreateView(CreateView):
    model = Patient
    form_class = PatientForm
    template_name = 'diagnostics/patients/patient_form.html'
    success_url = reverse_lazy('diagnostics:patient_list')

class PatientDetailView(DetailView):
    model = Patient
    template_name = 'diagnostics/patients/patient_detail.html'
    context_object_name = 'patient'

# --- IPD Admission Views ---

def ipd_admission_list(request):
    q = request.GET.get('q', '')
    status = request.GET.get('status', '')

    admissions = IPDAdmission.objects.select_related('visit__patient', 'current_bed', 'current_consultant')

    if q:
        admissions = admissions.filter(
            Q(visit__patient__name__icontains=q) |
            Q(visit__patient__mobile__icontains=q)
        )

    if status == 'admitted':
        admissions = admissions.filter(is_discharged=False)
    elif status == 'discharged':
        admissions = admissions.filter(is_discharged=True)

    paginator = Paginator(admissions.order_by('-admission_date'), 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'diagnostics/ipd/ipd_admission_list.html', {
        'admissions': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages()
    })
@require_http_methods(["GET", "POST"])
def ipd_admission_create_or_update(request, admission_code=None):
    if admission_code:
        admission = get_object_or_404(IPDAdmission, admission_code=admission_code)
        visit = admission.visit
        patient = visit.patient
        edit_mode = True
    else:
        admission = IPDAdmission()
        visit = PatientVisit()
        patient = Patient()
        edit_mode = False

    if request.method == "POST":
        patient_form = PatientForm(request.POST, instance=patient)
        visit_form = PatientVisitForm(request.POST, instance=visit)
        ipd_form = IPDAdmissionForm(request.POST, instance=admission)

        if all([patient_form.is_valid(), visit_form.is_valid(), ipd_form.is_valid()]):
            patient = patient_form.save()
            visit = visit_form.save(commit=False)
            visit.patient = patient
            visit.save()

            admission = ipd_form.save(commit=False)
            admission.patient = patient
            admission.visit = visit
            admission.save()

            return JsonResponse({
                'success': True,
                'message': f'Admission {"updated" if edit_mode else "created"} successfully.'
            })

        return JsonResponse({
            'success': False,
            'errors': {
                'patient': patient_form.errors,
                'visit': visit_form.errors,
                'ipd': ipd_form.errors,
            }
        })

    # GET request — render form
    context = {
        'patient_form': PatientForm(instance=patient),
        'visit_form': PatientVisitForm(instance=visit),
        'ipd_form': IPDAdmissionForm(instance=admission),
        'consultants': Consultant.objects.all(),
        'beds': Bed.objects.filter(status='available'),
        'edit_mode': edit_mode,
        'admission': admission if edit_mode else None,
    }
    return render(request, 'diagnostics/ipd/ipd_admission_form.html', context)
def fetch_patient_by_mobile_or_code(request):
    query = request.GET.get('query', '')
    patient = Patient.objects.filter(mobile=query).first() or Patient.objects.filter(patient_code=query).first()
    if patient:
        return JsonResponse({
            'found': True,
            'name': patient.name,
            'age': patient.age,
            'gender': patient.gender,
            'mobile': patient.mobile,
            'address': patient.address,
            'patient_code': patient.patient_code
        })
    return JsonResponse({'found': False})
def get_available_beds(request):
    bed_type = request.GET.get('type')
    beds = Bed.objects.select_related('bed_type')

    if bed_type:
        beds = beds.filter(bed_type__name=bed_type)

    bed_data = []
    for bed in beds:
        # Determine status
        if bed.ipdadmission_set.filter(is_discharged=False).exists():
            status = "Occupied"
        elif bed.status == "cleaning":
            status = "Cleaning"
        elif bed.status == "reserved":
            status = "Reserved"
        else:
            status = "Available"

        bed_data.append({
            'id': bed.id,
            'name': bed.name,
            'type': bed.bed_type.name if bed.bed_type else '',
            'rate': str(bed.daily_rate),
            'status': status
        })

    return JsonResponse({'beds': bed_data})
def check_bed_availability(request):
    bed_id = request.GET.get('bed_id')
    try:
        bed = Bed.objects.get(id=bed_id)
        is_occupied = bed.ipdadmission_set.filter(is_discharged=False).exists()
        return JsonResponse({'available': not is_occupied})
    except Bed.DoesNotExist:
        return JsonResponse({'available': False})

    mobile = request.POST.get('mobile')
    patient = Patient.objects.filter(mobile=mobile).first()

    if patient:
        visit_form = PatientVisitForm(request.POST)
        ipd_form = IPDAdmissionForm(request.POST)
    else:
        patient_form = PatientForm(request.POST)
        visit_form = PatientVisitForm(request.POST)
        ipd_form = IPDAdmissionForm(request.POST)

        if not patient_form.is_valid():
            return JsonResponse({'success': False, 'errors': {'patient': patient_form.errors}}, status=400)

        patient = patient_form.save(commit=False)
        patient.created_by = request.user
        patient.updated_by = request.user
        patient.save()

    if visit_form.is_valid() and ipd_form.is_valid():
        visit = visit_form.save(commit=False)
        visit.patient = patient
        visit.created_by = request.user
        visit.save()

        ipd = ipd_form.save(commit=False)
        ipd.visit = visit
        ipd.created_by = request.user
        ipd.save()

        return JsonResponse({'success': True, 'redirect_url': '/ipd/admissions/'})
    else:
        return JsonResponse({
            'success': False,
            'errors': {
                'visit': visit_form.errors,
                'ipd': ipd_form.errors
            }
        }, status=400)

# Invoice Management Views
def invoice_list(request):
    from_date = request.GET.get('from')
    to_date = request.GET.get('to')
    selected_user = request.GET.get('user')
    payment_status = request.GET.get('status', 'All')
    page_number = request.GET.get('page', 1)

    invoices = AdviceInvoice.objects.select_related('visit__patient', 'visit__consultant', 'created_by')

    if from_date and to_date:
        try:
            from_dt = datetime.strptime(from_date, '%Y-%m-%d')
            to_dt = datetime.strptime(to_date, '%Y-%m-%d')
            invoices = invoices.filter(visit__visit_date__date__range=(from_dt, to_dt))
        except ValueError:
            pass

    if selected_user and selected_user != 'All':
        invoices = invoices.filter(created_by__username=selected_user)

    if payment_status == 'Paid':
        invoices = invoices.filter(is_paid=True)
    elif payment_status == 'Due':
        invoices = invoices.filter(is_paid=False)

    invoices = invoices.order_by('-id')
    paginator = Paginator(invoices, 20)
    page_obj = paginator.get_page(page_number)

    users = CustomUser.objects.values_list('username', flat=True)

    return render(request, 'diagnostics/billing/invoice_list.html', {
        'page_obj': page_obj,
        'users': users,
        'selected_user': selected_user,
        'from_date': from_date,
        'to_date': to_date,
        'payment_status': payment_status,
    })

def invoice_view(request, visit_code):
    invoice = get_object_or_404(
        AdviceInvoice.objects.select_related('visit__patient', 'visit__consultant', 'created_by'),
        visit__visit_code=visit_code
    )

    copy_type = request.GET.get('copy', 'view')

    context = {
        'invoice': invoice,
        'copy_type': copy_type,
    }

    return render(request, 'diagnostics/billing/invoice_detail.html', context)

# Collection Management View
def collection_list(request):
    from_date = request.GET.get('from')
    to_date = request.GET.get('to')
    selected_user = request.GET.get('user')
    page_number = request.GET.get('page', 1)

    # Base queryset
    payments = Payment.objects.select_related('created_by', 'invoice') \
        .prefetch_related(Prefetch(
            'paymentmethod_set',
            queryset=PaymentMethod.objects.select_related('method_type')
        ))

    # Date filter
    if from_date and to_date:
        try:
            from_dt = datetime.strptime(from_date, '%Y-%m-%d')
            to_dt = datetime.strptime(to_date, '%Y-%m-%d')
            payments = payments.filter(paid_on__date__range=(from_dt, to_dt))
        except ValueError:
            pass

    # User filter
    if selected_user and selected_user != 'All':
        payments = payments.filter(created_by__username=selected_user)

    # Ordering
    payments = payments.order_by('-paid_on')

    # Pagination
    paginator = Paginator(payments, 20)
    page_obj = paginator.get_page(page_number)

    # visit_code → patient.name mapping
    visit_codes = [p.visit_code for p in page_obj]
    visit_map = {
        v.visit_code: v.patient.name
        for v in PatientVisit.objects.select_related('patient').filter(visit_code__in=visit_codes)
    }

    # User list for filter dropdown
    users = CustomUser.objects.values_list('username', flat=True)

    # Final context
    context = {
        'page_obj': page_obj,
        'visit_map': visit_map,
        'users': users,
        'selected_user': selected_user,
        'from_date': from_date,
        'to_date': to_date,
    }

    return render(request, 'diagnostics/billing/collection_list.html', context)

# Jasper Report Views can be added here if needed
import os

java_home = r"C:\Program Files\Java\jdk-17"
os.environ['JAVA_HOME'] = java_home
os.environ['PATH'] = java_home + r"\bin;" + java_home + r"\bin\server;" + os.environ['PATH']

def download_invoice(request, visit_code):
    if not visit_code:
        return HttpResponseBadRequest("Visit code is required.")

    pdf_filename = f"invoice_{visit_code}.pdf"
    pdf_path = os.path.join(BASE_DIR, 'reports', 'output', pdf_filename)

    # ✅ পুরনো ফাইল থাকলেও নতুন করে জেনারেট করব
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    generate_patient_invoice(visit_code, pdf_filename)

    if not os.path.exists(pdf_path):
        return HttpResponseServerError("PDF generation failed.")

    return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')

def generate_invoice_pdf(visit_code, copy_type, output_filename):
    input_file = os.path.join('reports', 'invoice_patient.jrxml')
    output_file = os.path.join('reports', 'output', output_filename.replace('.pdf', ''))
    logo_file = os.path.join(settings.BASE_DIR, 'static', 'profile_images', 'default_profile.png')
    subreport_file = os.path.join(settings.BASE_DIR, 'reports', 'sub_access_reports.jasper')

    db_connection = {
        'driver': 'mysql',
        'username': 'LabExpert',
        'password': 'LabExpert2025',
        'host': 'localhost',
        'database': 'dh_soft_db',
        'port': '3307',
    }

    parameters = {
        'visit_code': visit_code,
        'copy_type': copy_type,
        'img': logo_file,
        'sub': subreport_file,
    }

    report = PyReportJasper()
    report.config(
        input_file=input_file,
        output_file=output_file,
        output_formats=["pdf"],
        db_connection=db_connection,
        parameters=parameters
    )
    
    print("Generating report with parameters:")
    print("Input file:", input_file)
    print("Output file:", output_file)
    print("DB:", db_connection)
    print("Parameters:", parameters)
    print("Logo exists:", os.path.exists(logo_file))
    print("Subreport exists:", os.path.exists(subreport_file))

    report.process_report()

def invoice_print(request, visit_code):
    if not visit_code:
        return HttpResponseBadRequest("❌ Visit code is required.")

    copy_type = request.GET.get('copy', 'office')
    if copy_type not in ['office', 'patient']:
        copy_type = 'office'

    pdf_filename = f"invoice_{visit_code}_{copy_type}.pdf"
    output_dir = os.path.join(settings.BASE_DIR, 'reports', 'output')
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, pdf_filename)

    try:
        generate_invoice_pdf(visit_code, copy_type, pdf_filename)
    except Exception as e:
        import traceback
        print("❌ Jasper Error:\n", traceback.format_exc())
        return HttpResponseServerError(f"PDF generation failed: {e}")

    if not os.path.exists(pdf_path):
        return HttpResponseServerError("PDF file not found after generation.")

    return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
