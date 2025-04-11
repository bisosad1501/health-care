from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DoctorAvailabilityViewSet,
    TimeSlotViewSet,
    AppointmentViewSet,
    AppointmentReminderViewSet,
    test_endpoint
)

router = DefaultRouter()
router.register(r'doctor-availabilities', DoctorAvailabilityViewSet)
router.register(r'time-slots', TimeSlotViewSet)
router.register(r'appointments', AppointmentViewSet)
router.register(r'appointment-reminders', AppointmentReminderViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('test/', test_endpoint, name='test-endpoint'),  # Endpoint test đơn giản
]
