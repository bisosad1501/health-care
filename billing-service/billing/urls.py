from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    InvoiceViewSet, InvoiceItemViewSet, PaymentViewSet, InsuranceClaimViewSet,
    create_invoice_from_appointment_view, create_invoice_from_lab_test_view,
    create_invoice_from_prescription_view, create_invoice_from_medical_record_view
)

router = DefaultRouter()
router.register(r'invoices', InvoiceViewSet)
router.register(r'invoice-items', InvoiceItemViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'insurance-claims', InsuranceClaimViewSet)

urlpatterns = [
    path('', include(router.urls)),

    # API endpoints for creating invoices from other services
    path('create-from-appointment/', create_invoice_from_appointment_view, name='create-from-appointment'),
    path('create-from-lab-test/', create_invoice_from_lab_test_view, name='create-from-lab-test'),
    path('create-from-prescription/', create_invoice_from_prescription_view, name='create-from-prescription'),
    path('create-from-medical-record/', create_invoice_from_medical_record_view, name='create-from-medical-record'),
]
