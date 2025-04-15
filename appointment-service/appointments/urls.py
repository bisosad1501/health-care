from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DoctorAvailabilityViewSet,
    TimeSlotViewSet,
    AppointmentViewSet,
    AppointmentReminderViewSet,
    test_endpoint
)

# Router chính cho các endpoint cấp cao nhất
router = DefaultRouter()
router.register(r'appointments', AppointmentViewSet)

# Router cho các endpoint trong /appointments/
appointments_router = DefaultRouter()
appointments_router.register(r'doctor-availabilities', DoctorAvailabilityViewSet)
appointments_router.register(r'time-slots', TimeSlotViewSet)
appointments_router.register(r'reminders', AppointmentReminderViewSet)

# Hỗ trợ cả hai cấu trúc URL
urlpatterns = [
    # Cấu trúc URL cũ
    path('', include(router.urls)),

    # Đăng ký router cho các endpoint cũ
    path('doctor-availabilities/', DoctorAvailabilityViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('doctor-availabilities/<int:pk>/', DoctorAvailabilityViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})),
    path('doctor-availabilities/generate_time_slots/', DoctorAvailabilityViewSet.as_view({'post': 'generate_time_slots'})),
    path('time-slots/', TimeSlotViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('time-slots/<int:pk>/', TimeSlotViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})),
    path('appointment-reminders/', AppointmentReminderViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('appointment-reminders/<int:pk>/', AppointmentReminderViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})),

    # Cấu trúc URL mới (nested)
    path('appointments/', include(appointments_router.urls)),

    # Endpoint test
    path('test/', test_endpoint, name='test-endpoint'),
]
