from django.urls import path
from .views import (
    # User APIs
    UserListAPI, UserDetailAPI, CurrentUserAPI,

    # Document APIs
    UserDocumentListAPI, UserDocumentDetailAPI, VerifyDocumentAPI,

    # Address APIs
    AddressListAPI, AddressDetailAPI,

    # Contact Info APIs
    ContactInfoAPI,

    # Profile APIs
    PatientProfileAPI, DoctorProfileAPI, NurseProfileAPI,
    PharmacistProfileAPI, InsuranceProviderProfileAPI, LabTechnicianProfileAPI, AdminProfileAPI,

    # Preference APIs
    UserPreferenceAPI,

    # Activity APIs
    UserActivityListAPI,

    # Session APIs
    UserSessionListAPI, UserSessionDetailAPI,

    # Admin List APIs
    list_all_patient_profiles, list_all_doctor_profiles, list_all_nurse_profiles,
    list_all_pharmacist_profiles, list_all_insurance_provider_profiles, list_all_lab_technician_profiles
)

urlpatterns = [
    # User APIs
    path('users/', UserListAPI.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailAPI.as_view(), name='user-detail'),
    path('users/me/', CurrentUserAPI.as_view(), name='current-user'),

    # Document APIs
    path('documents/', UserDocumentListAPI.as_view(), name='document-list'),
    path('documents/<int:pk>/', UserDocumentDetailAPI.as_view(), name='document-detail'),
    path('documents/<int:pk>/verify/', VerifyDocumentAPI.as_view(), name='document-verify'),

    # Address APIs
    path('addresses/', AddressListAPI.as_view(), name='address-list'),
    path('addresses/<int:pk>/', AddressDetailAPI.as_view(), name='address-detail'),

    # Contact Info APIs
    path('contact-info/', ContactInfoAPI.as_view(), name='contact-info'),

    # Profile APIs
    path('patient-profile/', PatientProfileAPI.as_view(), name='patient-profile'),
    path('doctor-profile/', DoctorProfileAPI.as_view(), name='doctor-profile'),
    path('nurse-profile/', NurseProfileAPI.as_view(), name='nurse-profile'),
    path('pharmacist-profile/', PharmacistProfileAPI.as_view(), name='pharmacist-profile'),
    path('insurance-provider-profile/', InsuranceProviderProfileAPI.as_view(), name='insurance-provider-profile'),
    path('lab-technician-profile/', LabTechnicianProfileAPI.as_view(), name='lab-technician-profile'),
    path('admin-profile/', AdminProfileAPI.as_view(), name='admin-profile'),

    # Preference APIs
    path('preferences/', UserPreferenceAPI.as_view(), name='user-preferences'),

    # Activity APIs
    path('activities/', UserActivityListAPI.as_view(), name='user-activities'),

    # Session APIs
    path('sessions/', UserSessionListAPI.as_view(), name='user-sessions'),
    path('sessions/<int:pk>/', UserSessionDetailAPI.as_view(), name='user-session-detail'),

    # Admin List APIs
    path('admin/patient-profiles/', list_all_patient_profiles, name='all-patient-profiles'),
    path('admin/doctor-profiles/', list_all_doctor_profiles, name='all-doctor-profiles'),
    path('admin/nurse-profiles/', list_all_nurse_profiles, name='all-nurse-profiles'),
    path('admin/pharmacist-profiles/', list_all_pharmacist_profiles, name='all-pharmacist-profiles'),
    path('admin/insurance-provider-profiles/', list_all_insurance_provider_profiles, name='all-insurance-provider-profiles'),
    path('admin/lab-technician-profiles/', list_all_lab_technician_profiles, name='all-lab-technician-profiles'),
]
