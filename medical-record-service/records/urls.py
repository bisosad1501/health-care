from django.urls import path
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
    LabResultListCreateAPIView, LabResultDetailAPIView
)

urlpatterns = [
    # Medical Record endpoints
    path('medical-records/', MedicalRecordListCreateAPIView.as_view(), name='medical-record-list'),
    path('medical-records/<int:pk>/', MedicalRecordDetailAPIView.as_view(), name='medical-record-detail'),
    path('medical-records/<int:pk>/summary/', MedicalRecordSummaryAPIView.as_view(), name='medical-record-summary'),

    # Encounter endpoints
    path('encounters/', EncounterListCreateAPIView.as_view(), name='encounter-list'),
    path('encounters/<int:pk>/', EncounterDetailAPIView.as_view(), name='encounter-detail'),

    # Diagnosis endpoints
    path('diagnoses/', DiagnosisListCreateAPIView.as_view(), name='diagnosis-list'),
    path('diagnoses/<int:pk>/', DiagnosisDetailAPIView.as_view(), name='diagnosis-detail'),

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
