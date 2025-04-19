from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DoctorAvailabilityViewSet,
    TimeSlotViewSet,
    AppointmentViewSet,
    AppointmentReminderViewSet,
    PatientVisitViewSet,
    AppointmentReasonViewSet,
    test_endpoint,
    appointment_types,
    priorities,
    locations,
    doctor_working_days,
    available_doctors,
    specialties,
    departments,
    patient_insurance,
    verify_insurance
)

# Router chính cho các endpoint cấp cao nhất
router = DefaultRouter()
router.register(r'appointments', AppointmentViewSet)
router.register(r'patient-visits', PatientVisitViewSet)
router.register(r'appointment-reasons', AppointmentReasonViewSet)

# Router cho các endpoint trong /appointments/
appointments_router = DefaultRouter()
appointments_router.register(r'doctor-availabilities', DoctorAvailabilityViewSet)
appointments_router.register(r'time-slots', TimeSlotViewSet)
appointments_router.register(r'reminders', AppointmentReminderViewSet)
appointments_router.register(r'visits', PatientVisitViewSet)

# Hỗ trợ cả hai cấu trúc URL
urlpatterns = [
    # Cấu trúc URL cũ
    path('', include(router.urls)),

    # Đăng ký router cho các endpoint cũ
    path('doctor-availabilities/', DoctorAvailabilityViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('doctor-availabilities/<int:pk>/', DoctorAvailabilityViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})),
    path('doctor-availabilities/generate_time_slots/', DoctorAvailabilityViewSet.as_view({'post': 'generate_time_slots'})),
    path('doctor-availabilities/create_schedule/', DoctorAvailabilityViewSet.as_view({'post': 'create_schedule'})),
    path('time-slots/', TimeSlotViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('time-slots/<int:pk>/', TimeSlotViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})),
    path('appointment-reminders/', AppointmentReminderViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('appointment-reminders/<int:pk>/', AppointmentReminderViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})),
    path('patient-visits/', PatientVisitViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('patient-visits/<int:pk>/', PatientVisitViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})),
    path('patient-visits/check-in/', PatientVisitViewSet.as_view({'post': 'check_in'})),

    # Cấu trúc URL mới (nested)
    path('appointments/', include(appointments_router.urls)),

    # Endpoint test
    path('test/', test_endpoint, name='test-endpoint'),

    # Endpoint cho các loại khám bệnh, mức độ ưu tiên và địa điểm
    path('appointment-types/', appointment_types, name='appointment-types'),
    path('priorities/', priorities, name='priorities'),
    path('locations/', locations, name='locations'),

    # Endpoint cho lịch làm việc của bác sĩ
    path('doctor-working-days/', doctor_working_days, name='doctor-working-days'),

    # Endpoint cho danh sách bác sĩ có lịch trống
    path('doctors/available/', available_doctors, name='available-doctors'),

    # Endpoint cho danh sách chuyên khoa và khoa
    path('specialties/', specialties, name='specialties'),
    path('departments/', departments, name='departments'),

    # Endpoint cho bảo hiểm
    path('patient-insurance/', patient_insurance, name='patient-insurance'),
    path('verify-insurance/', verify_insurance, name='verify-insurance'),
]
