from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, UserDocumentViewSet, AddressViewSet, ContactInfoViewSet,
    PatientProfileViewSet, DoctorProfileViewSet, NurseProfileViewSet,
    PharmacistProfileViewSet, InsuranceProviderProfileViewSet, LabTechnicianProfileViewSet,
    AdminProfileViewSet, InsuranceInformationViewSet, SpecialtyViewSet, DepartmentViewSet,
    DoctorListViewSet
)
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from authentication.models import User
from .serializers import UserDetailSerializer

# Tạo router cho các ViewSet
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'documents', UserDocumentViewSet, basename='document')
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'contact-info', ContactInfoViewSet, basename='contact-info')
router.register(r'patient-profile', PatientProfileViewSet, basename='patient-profile')
router.register(r'doctor-profile', DoctorProfileViewSet, basename='doctor-profile')
router.register(r'nurse-profile', NurseProfileViewSet, basename='nurse-profile')
router.register(r'pharmacist-profile', PharmacistProfileViewSet, basename='pharmacist-profile')
router.register(r'insurance-provider-profile', InsuranceProviderProfileViewSet, basename='insurance-provider-profile')
router.register(r'lab-technician-profile', LabTechnicianProfileViewSet, basename='lab-technician-profile')
router.register(r'admin-profile', AdminProfileViewSet, basename='admin-profile')
router.register(r'insurance-information', InsuranceInformationViewSet, basename='insurance-information')
router.register(r'specialties', SpecialtyViewSet, basename='specialties')
router.register(r'departments', DepartmentViewSet, basename='departments')
router.register(r'doctors', DoctorListViewSet, basename='doctors')

# Hàm view để xử lý route /api/users/doctors/{doctor_id}/
@csrf_exempt
@api_view(['GET'])
def doctor_user_info(request, doctor_id):
    """
    Lấy thông tin người dùng của bác sĩ.
    Endpoint này được tạo để tương thích với medical-record-service.
    """
    try:
        # Tìm người dùng với ID và role là DOCTOR
        user = User.objects.get(id=doctor_id, role='DOCTOR')
        serializer = UserDetailSerializer(user)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response(
            {"detail": f"Doctor with ID {doctor_id} not found"},
            status=404
        )
    except Exception as e:
        return Response(
            {"detail": f"Error retrieving doctor info: {str(e)}"},
            status=400
        )

urlpatterns = [
    # Bao gồm tất cả các URL từ router
    path('', include(router.urls)),

    # Thêm route đặc biệt cho medical-record-service
    path('users/doctors/<int:doctor_id>/', doctor_user_info, name='doctor-user-info'),
]
