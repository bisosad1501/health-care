from django.urls import path, include
from rest_framework.routers import DefaultRouter
from common_auth import register_health_check
from .views import (
    MedicalRecordListCreateAPIView, MedicalRecordDetailAPIView, MedicalRecordSummaryAPIView,
    EncounterListCreateAPIView, EncounterDetailAPIView,
    DiagnosisListCreateAPIView, DiagnosisDetailAPIView,
    TreatmentListCreateAPIView, TreatmentDetailAPIView,
    AllergyListCreateAPIView, AllergyDetailAPIView,
    ImmunizationListCreateAPIView, ImmunizationDetailAPIView,
    MedicalHistoryListCreateAPIView, MedicalHistoryDetailAPIView,
    MedicationListCreateAPIView, MedicationDetailAPIView,
    VitalSignListCreateAPIView, VitalSignDetailAPIView,
    LabTestListCreateAPIView, LabTestDetailAPIView,
    LabResultListCreateAPIView, LabResultDetailAPIView,
    create_encounter_from_appointment
)

# Tạo router cho DiagnosisDetailAPIView
diagnosis_router = DefaultRouter()
diagnosis_router.register(r'diagnoses', DiagnosisDetailAPIView, basename='diagnosis')

urlpatterns = [
    # Medical Record endpoints
    path('medical-records/', MedicalRecordListCreateAPIView.as_view(), name='medical-record-list'),
    path('medical-records/<int:pk>/', MedicalRecordDetailAPIView.as_view(), name='medical-record-detail'),
    path('medical-records/<int:pk>/summary/', MedicalRecordSummaryAPIView.as_view(), name='medical-record-summary'),

    # Encounter endpoints
    path('encounters/', EncounterListCreateAPIView.as_view(), name='encounter-list'),
    path('encounters/<int:pk>/', EncounterDetailAPIView.as_view(), name='encounter-detail'),
    path('encounters/from-appointment/<int:appointment_id>/', create_encounter_from_appointment, name='create-encounter-from-appointment-alt'),

    # Diagnosis endpoints
    path('diagnoses/', DiagnosisListCreateAPIView.as_view(), name='diagnosis-list'),
    # Sử dụng router cho DiagnosisDetailAPIView
    path('', include(diagnosis_router.urls)),

    # Treatment endpoints
    path('treatments/', TreatmentListCreateAPIView.as_view(), name='treatment-list'),
    path('treatments/<int:pk>/', TreatmentDetailAPIView.as_view(), name='treatment-detail'),

    # Allergy endpoints
    path('allergies/', AllergyListCreateAPIView.as_view(), name='allergy-list'),
    path('allergies/<int:pk>/', AllergyDetailAPIView.as_view(), name='allergy-detail'),

    # Immunization endpoints
    path('immunizations/', ImmunizationListCreateAPIView.as_view(), name='immunization-list'),
    path('immunizations/<int:pk>/', ImmunizationDetailAPIView.as_view(), name='immunization-detail'),

    # Medical History endpoints
    path('medical-histories/', MedicalHistoryListCreateAPIView.as_view(), name='medical-history-list'),
    path('medical-histories/<int:pk>/', MedicalHistoryDetailAPIView.as_view(), name='medical-history-detail'),

    # Medication endpoints
    path('medications/', MedicationListCreateAPIView.as_view(), name='medication-list'),
    path('medications/<int:pk>/', MedicationDetailAPIView.as_view(), name='medication-detail'),

    # Vital Sign endpoints
    path('vital-signs/', VitalSignListCreateAPIView.as_view(), name='vital-sign-list'),
    path('vital-signs/<int:pk>/', VitalSignDetailAPIView.as_view(), name='vital-sign-detail'),

    # Lab Test endpoints
    path('lab-tests/', LabTestListCreateAPIView.as_view(), name='lab-test-list'),
    path('lab-tests/<int:pk>/', LabTestDetailAPIView.as_view(), name='lab-test-detail'),

    # Lab Result endpoints
    path('lab-results/', LabResultListCreateAPIView.as_view(), name='lab-result-list'),
    path('lab-results/<int:pk>/', LabResultDetailAPIView.as_view(), name='lab-result-detail'),
]

# Register health check endpoint
urlpatterns = register_health_check(urlpatterns)
