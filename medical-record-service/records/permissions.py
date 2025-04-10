"""
Proxy module for permissions from common-auth package.
This file exists to maintain backward compatibility.
"""
from common_auth.permissions import MedicalRecordPermissions, IsAdmin, IsDoctor, IsNurse, IsPatient, IsLabTechnician, IsPharmacist

# Re-export for backward compatibility
CanViewMedicalRecords = MedicalRecordPermissions.CanViewMedicalRecords
CanCreateMedicalRecord = MedicalRecordPermissions.CanCreateMedicalRecord
CanUpdateMedicalRecord = MedicalRecordPermissions.CanUpdateMedicalRecord
CanDeleteMedicalRecord = MedicalRecordPermissions.CanDeleteMedicalRecord
CanShareMedicalRecord = MedicalRecordPermissions.CanShareMedicalRecord
