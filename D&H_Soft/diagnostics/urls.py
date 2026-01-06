from django.urls import path
from . import views

app_name = "diagnostics"

urlpatterns = [
    # Test Management URLs
    path('test_categories/', views.test_category_list, name='test_category_list'),
    path('test_categories/create/', views.test_category_create, name='test_category_create'),
    path('test_categories/<int:pk>/edit/', views.test_category_edit, name='test_category_edit'),
    path('test_categories/<int:pk>/delete/', views.test_category_delete, name='test_category_delete'),
    path('test_categories/subcategories/', views.get_subcategories, name='ajax_subcategories'),
    path('test_categories/<int:pk>/groups/', views.test_category_groups, name='test_category_groups'),
    path('test_groups/', views.test_group_manager, name='test_group_list'),
    path('test_groups/create/', views.test_group_form, name='test_group_create'),
    path('test_groups/<int:pk>/edit/', views.test_group_form, name='test_group_edit'),
    path('test_items/', views.test_item_list, name='test_item_list'),
    path('test_items/create/', views.test_item_create, name='test_item_create'),

    # Patient URLs
    path('patients/', views.PatientListView.as_view(), name='patient_list'),
    path('patients/create/', views.PatientCreateView.as_view(), name='patient_create'),
    path('patients/<int:pk>/', views.PatientDetailView.as_view(), name='patient_detail'),
    
    # Consultant URLs
   # path('consultants/', views.ConsultantListView.as_view(), name='ConsultantReferrerList'),
    #path('consultants/create/', views.ConsultantCreateView.as_view(), name='consultant_create'),
    #path('consultants/<int:pk>/edit/', views.ConsultantUpdateView.as_view(), name='consultant_edit'),
    path('ajax/consultant-search/', views.consultant_search, name='consultant_search'),

    # IPD Admission URLs
    path('ipd/admissions/', views.ipd_admission_list, name='ipd_admission_list'),
    path('ipd/admission/submit/', views.ipd_admission_create_or_update, name='ipd_admission_create'),
    path('ipd/admission/<str:admission_code>/edit/', views.ipd_admission_create_or_update, name='ipd_admission_edit'),
    path('ipd/fetch-patient/', views.fetch_patient_by_mobile_or_code, name='fetch_patient'),
    path('ipd/check-bed/', views.check_bed_availability, name='check_bed'),
    path('ipd/available-beds/', views.get_available_beds, name='available_beds'),

    # Invoice Mangement URLs# urls.py
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/detail/<str:visit_code>/', views.invoice_view, name='invoice_view'),
    path('invoices/<str:visit_code>/print/', views.invoice_print, name='invoice_print'),

    path('invoices/<str:visit_code>/download/', views.download_invoice, name='download_invoice'),
    path('invoices/collection/', views.collection_list, name='collection_list'),

    # Patient Report URLs
    path('reports/', views.patient_report_list, name='report_patient_list'), 
    path('reports/<int:visit_id>/', views.patient_report_detail, name='report_detail'),
]