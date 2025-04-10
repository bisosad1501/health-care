from django.contrib import admin
from .models import Address, ContactInfo, PatientProfile, DoctorProfile, NurseProfile

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'street', 'city', 'state', 'postal_code', 'country', 'is_primary')
    search_fields = ('user__email', 'street', 'city', 'state', 'postal_code', 'country')
    list_filter = ('is_primary', 'country', 'state', 'city')

@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'emergency_contact_name', 'emergency_contact_phone')
    search_fields = ('user__email', 'phone_number', 'emergency_contact_name', 'emergency_contact_phone')

@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_of_birth', 'gender', 'blood_type')
    search_fields = ('user__email', 'blood_type', 'allergies', 'medical_conditions')
    list_filter = ('gender', 'blood_type')

@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'license_number', 'years_of_experience')
    search_fields = ('user__email', 'specialization', 'license_number', 'education')
    list_filter = ('specialization', 'years_of_experience')

@admin.register(NurseProfile)
class NurseProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number', 'department')
    search_fields = ('user__email', 'license_number', 'department')
    list_filter = ('department',)
