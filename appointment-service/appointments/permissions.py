"""
Proxy module for permissions from common-auth package.
This file exists to maintain backward compatibility.
"""
from common_auth.permissions import AppointmentPermissions, IsAdmin, IsDoctor, IsNurse, IsPatient

# Re-export for backward compatibility
CanViewAppointments = AppointmentPermissions.CanViewAppointments
CanCreateAppointment = AppointmentPermissions.CanCreateAppointment
CanUpdateAppointment = AppointmentPermissions.CanUpdateAppointment
CanDeleteAppointment = AppointmentPermissions.CanDeleteAppointment
CanManageDoctorSchedule = AppointmentPermissions.CanManageDoctorSchedule

# Legacy classes - mapped to new permissions for backward compatibility
class IsPatientOrDoctor:
    def __new__(cls):
        return CanViewAppointments()

class IsDoctor(IsDoctor):
    """
    Permission to only allow doctors to access their availabilities and time slots.
    """
    pass

# Use IsAdmin directly from common-auth
# No need to redefine
