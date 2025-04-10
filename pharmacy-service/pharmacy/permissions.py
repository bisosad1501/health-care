"""
Proxy module for permissions from common-auth package.
This file exists to maintain backward compatibility.
"""
from common_auth.permissions import PharmacyPermissions, IsAdmin, IsDoctor, IsPatient, IsPharmacist

# Re-export for backward compatibility
CanViewPrescriptions = PharmacyPermissions.CanViewPrescriptions
CanCreatePrescription = PharmacyPermissions.CanCreatePrescription
CanUpdatePrescription = PharmacyPermissions.CanUpdatePrescription
CanCancelPrescription = PharmacyPermissions.CanCancelPrescription
CanManageMedication = PharmacyPermissions.CanManageMedication
