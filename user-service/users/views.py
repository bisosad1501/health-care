from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q
from authentication.models import User
from common_auth.permissions import IsAuthenticated, HasRole, HasResourceAccess
from .models import (
    Address, ContactInfo, UserDocument, PatientProfile, DoctorProfile, NurseProfile,
    PharmacistProfile, InsuranceInformation, InsuranceProviderProfile, LabTechnicianProfile,
    AdminProfile, UserPreference, UserActivity, UserSession
)
from .serializers import (
    UserDetailSerializer, UserBasicSerializer,
    AddressSerializer, ContactInfoSerializer, UserDocumentSerializer,
    PatientProfileSerializer, DoctorProfileSerializer, NurseProfileSerializer,
    PharmacistProfileSerializer, InsuranceInformationSerializer, InsuranceProviderProfileSerializer,
    LabTechnicianProfileSerializer, AdminProfileSerializer,
    UserPreferenceSerializer, UserActivitySerializer, UserSessionSerializer
)

# ============================================================
# User APIs
# ============================================================

class UserListAPI(APIView):
    """
    API endpoint để lấy danh sách người dùng hoặc tạo người dùng mới.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Lấy danh sách người dùng"""
        # Admin có thể xem tất cả người dùng, người dùng khác chỉ xem thông tin của mình
        if request.user.role == 'ADMIN':
            users = User.objects.all()
        else:
            users = User.objects.filter(id=request.user.id)

        serializer = UserDetailSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Tạo người dùng mới (chỉ dành cho admin)"""
        if request.user.role != 'ADMIN':
            return Response(
                {"detail": "Only administrators can create users."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = UserDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailAPI(APIView):
    """
    API endpoint để xem, cập nhật hoặc xóa thông tin người dùng.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        """Lấy đối tượng người dùng dựa trên ID"""
        try:
            user = User.objects.get(pk=pk)
            # Kiểm tra quyền truy cập
            if self.request.user.role != 'ADMIN' and self.request.user.id != user.id:
                raise ValidationError({"detail": "You do not have permission to access this user."})
            return user
        except User.DoesNotExist:
            raise ValidationError({"detail": "User not found."})

    def get(self, request, pk):
        """Lấy thông tin chi tiết của người dùng"""
        user = self.get_object(pk)
        serializer = UserDetailSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk):
        """Cập nhật thông tin người dùng"""
        user = self.get_object(pk)
        serializer = UserDetailSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Xóa người dùng"""
        # Chỉ admin mới có quyền xóa người dùng
        if request.user.role != 'ADMIN':
            return Response(
                {"detail": "Only administrators can delete users."},
                status=status.HTTP_403_FORBIDDEN
            )

        user = self.get_object(pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CurrentUserAPI(APIView):
    """
    API endpoint để lấy thông tin người dùng hiện tại.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Lấy thông tin người dùng hiện tại"""
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)

# ============================================================
# User Document APIs
# ============================================================

class UserDocumentListAPI(APIView):
    """
    API endpoint để lấy danh sách tài liệu hoặc tạo tài liệu mới.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Lấy danh sách tài liệu của người dùng hiện tại"""
        if request.user.role == 'ADMIN':
            # Admin có thể xem tất cả tài liệu hoặc lọc theo người dùng
            user_id = request.query_params.get('user_id')
            if user_id:
                documents = UserDocument.objects.filter(user_id=user_id)
            else:
                documents = UserDocument.objects.all()
        else:
            # Người dùng thường chỉ xem tài liệu của mình
            documents = UserDocument.objects.filter(user=request.user)

        serializer = UserDocumentSerializer(documents, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Tạo tài liệu mới"""
        # Xác định người dùng cho tài liệu
        data = request.data.copy()

        # Nếu là admin và cung cấp user_id, sử dụng user_id đó
        if request.user.role == 'ADMIN' and 'user' in data:
            pass  # Giữ nguyên user_id được cung cấp
        else:
            # Người dùng thường chỉ có thể tạo tài liệu cho chính mình
            data['user'] = request.user.id

        serializer = UserDocumentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDocumentDetailAPI(APIView):
    """
    API endpoint để xem, cập nhật hoặc xóa tài liệu.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        """Lấy đối tượng tài liệu dựa trên ID"""
        try:
            document = UserDocument.objects.get(pk=pk)
            # Kiểm tra quyền truy cập
            if document.user.id != self.request.user.id and self.request.user.role != 'ADMIN':
                raise ValidationError({"detail": "You do not have permission to access this document."})
            return document
        except UserDocument.DoesNotExist:
            raise ValidationError({"detail": "Document not found."})

    def get(self, request, pk):
        """Lấy thông tin chi tiết của tài liệu"""
        document = self.get_object(pk)
        serializer = UserDocumentSerializer(document)
        return Response(serializer.data)

    def put(self, request, pk):
        """Cập nhật thông tin tài liệu"""
        document = self.get_object(pk)
        serializer = UserDocumentSerializer(document, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Xóa tài liệu"""
        document = self.get_object(pk)
        document.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class VerifyDocumentAPI(APIView):
    """
    API endpoint để xác minh tài liệu (chỉ dành cho admin).
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        """Xác minh tài liệu"""
        if request.user.role != 'ADMIN':
            return Response(
                {"detail": "Only administrators can verify documents."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            document = UserDocument.objects.get(pk=pk)
            notes = request.data.get('verification_notes', '')
            document.verify(notes)
            serializer = UserDocumentSerializer(document)
            return Response(serializer.data)
        except UserDocument.DoesNotExist:
            return Response({"detail": "Document not found."}, status=status.HTTP_404_NOT_FOUND)

# ============================================================
# Address APIs
# ============================================================

class AddressListAPI(APIView):
    """
    API endpoint để lấy danh sách địa chỉ hoặc tạo địa chỉ mới.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Lấy danh sách địa chỉ của người dùng hiện tại"""
        addresses = Address.objects.filter(user=request.user)
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Tạo địa chỉ mới cho người dùng hiện tại"""
        data = request.data.copy()
        data['user'] = request.user.id

        serializer = AddressSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddressDetailAPI(APIView):
    """
    API endpoint để xem, cập nhật hoặc xóa địa chỉ.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        """Lấy đối tượng địa chỉ dựa trên ID"""
        try:
            address = Address.objects.get(pk=pk)
            # Kiểm tra quyền truy cập
            if address.user.id != self.request.user.id and self.request.user.role != 'ADMIN':
                raise ValidationError({"detail": "You do not have permission to access this address."})
            return address
        except Address.DoesNotExist:
            raise ValidationError({"detail": "Address not found."})

    def get(self, request, pk):
        """Lấy thông tin chi tiết của địa chỉ"""
        address = self.get_object(pk)
        serializer = AddressSerializer(address)
        return Response(serializer.data)

    def put(self, request, pk):
        """Cập nhật thông tin địa chỉ"""
        address = self.get_object(pk)
        serializer = AddressSerializer(address, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Xóa địa chỉ"""
        address = self.get_object(pk)
        address.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# ============================================================
# Contact Info APIs
# ============================================================

class ContactInfoAPI(APIView):
    """
    API endpoint để quản lý thông tin liên hệ của người dùng.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Lấy thông tin liên hệ của người dùng hiện tại"""
        try:
            contact_info = ContactInfo.objects.get(user=request.user)
            serializer = ContactInfoSerializer(contact_info)
            return Response(serializer.data)
        except ContactInfo.DoesNotExist:
            return Response({"detail": "Contact information not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """Tạo thông tin liên hệ mới cho người dùng hiện tại"""
        # Kiểm tra xem người dùng đã có thông tin liên hệ chưa
        if ContactInfo.objects.filter(user=request.user).exists():
            return Response(
                {"detail": "User already has contact information. Use PUT to update."},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = request.data.copy()
        data['user'] = request.user.id

        serializer = ContactInfoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """Cập nhật thông tin liên hệ của người dùng hiện tại"""
        try:
            contact_info = ContactInfo.objects.get(user=request.user)
            serializer = ContactInfoSerializer(contact_info, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ContactInfo.DoesNotExist:
            return Response(
                {"detail": "Contact information not found. Use POST to create."},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request):
        """Xóa thông tin liên hệ của người dùng hiện tại"""
        try:
            contact_info = ContactInfo.objects.get(user=request.user)
            contact_info.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ContactInfo.DoesNotExist:
            return Response({"detail": "Contact information not found."}, status=status.HTTP_404_NOT_FOUND)

# ============================================================
# Patient Profile APIs
# ============================================================

class PatientProfileAPI(APIView):
    """
    API endpoint để quản lý hồ sơ bệnh nhân.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Lấy hồ sơ bệnh nhân của người dùng hiện tại"""
        try:
            profile = PatientProfile.objects.get(user_id=request.user.id)
            serializer = PatientProfileSerializer(profile)
            return Response(serializer.data)
        except PatientProfile.DoesNotExist:
            return Response({"detail": "Patient profile not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """Tạo hồ sơ bệnh nhân mới cho người dùng hiện tại"""
        # Kiểm tra vai trò người dùng
        if request.user.role != 'PATIENT':
            return Response(
                {"detail": "Only users with PATIENT role can create patient profiles."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Kiểm tra xem người dùng đã có hồ sơ bệnh nhân chưa
        if PatientProfile.objects.filter(user_id=request.user.id).exists():
            return Response(
                {"detail": "User already has a patient profile. Use PUT to update."},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = request.data.copy()
        data['user'] = request.user.id

        serializer = PatientProfileSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """Cập nhật hồ sơ bệnh nhân của người dùng hiện tại"""
        try:
            profile = PatientProfile.objects.get(user_id=request.user.id)
            serializer = PatientProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except PatientProfile.DoesNotExist:
            return Response(
                {"detail": "Patient profile not found. Use POST to create."},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request):
        """Xóa hồ sơ bệnh nhân của người dùng hiện tại"""
        try:
            profile = PatientProfile.objects.get(user=request.user)
            profile.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except PatientProfile.DoesNotExist:
            return Response({"detail": "Patient profile not found."}, status=status.HTTP_404_NOT_FOUND)

# ============================================================
# Doctor Profile APIs
# ============================================================

class DoctorProfileAPI(APIView):
    """
    API endpoint để quản lý hồ sơ bác sĩ.
    """
    permission_classes = [IsAuthenticated, HasRole(['DOCTOR', 'ADMIN'])]

    def get(self, request):
        """Lấy hồ sơ bác sĩ của người dùng hiện tại"""
        try:
            profile = DoctorProfile.objects.get(user=request.user)
            serializer = DoctorProfileSerializer(profile)
            return Response(serializer.data)
        except DoctorProfile.DoesNotExist:
            return Response({"detail": "Doctor profile not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """Tạo hồ sơ bác sĩ mới cho người dùng hiện tại"""
        # Kiểm tra vai trò người dùng
        if request.user.role != 'DOCTOR':
            return Response(
                {"detail": "Only users with DOCTOR role can create doctor profiles."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Kiểm tra xem người dùng đã có hồ sơ bác sĩ chưa
        if DoctorProfile.objects.filter(user=request.user).exists():
            return Response(
                {"detail": "User already has a doctor profile. Use PUT to update."},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = request.data.copy()
        data['user'] = request.user.id

        serializer = DoctorProfileSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """Cập nhật hồ sơ bác sĩ của người dùng hiện tại"""
        try:
            profile = DoctorProfile.objects.get(user=request.user)
            serializer = DoctorProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except DoctorProfile.DoesNotExist:
            return Response(
                {"detail": "Doctor profile not found. Use POST to create."},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request):
        """Xóa hồ sơ bác sĩ của người dùng hiện tại"""
        try:
            profile = DoctorProfile.objects.get(user=request.user)
            profile.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except DoctorProfile.DoesNotExist:
            return Response({"detail": "Doctor profile not found."}, status=status.HTTP_404_NOT_FOUND)

# ============================================================
# Admin User Management APIs
# ============================================================

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_staff_user(request):
    """
    API endpoint để quản trị viên tạo tài khoản cho nhân viên y tế.
    Chỉ quản trị viên mới có thể truy cập endpoint này.
    """
    # Kiểm tra quyền quản trị viên
    if request.user.role != 'ADMIN':
        return Response(
            {"detail": "Only administrators can create staff accounts."},
            status=status.HTTP_403_FORBIDDEN
        )

    # Lấy dữ liệu từ request
    data = request.data
    role = data.get('role')

    # Kiểm tra vai trò hợp lệ
    valid_roles = ['DOCTOR', 'NURSE', 'PHARMACIST', 'LAB_TECH', 'INSURANCE', 'ADMIN']
    if not role or role not in valid_roles:
        return Response(
            {"detail": f"Invalid role. Must be one of: {', '.join(valid_roles)}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Tạo mật khẩu ngẫu nhiên nếu không được cung cấp
    if not data.get('password'):
        import string
        import random
        chars = string.ascii_letters + string.digits
        data['password'] = ''.join(random.choice(chars) for _ in range(10))

    # Tạo người dùng mới
    try:
        user = User.objects.create_user(
            email=data.get('email'),
            password=data.get('password'),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            role=role
        )

        # Tạo hồ sơ tương ứng với vai trò và thông tin được cung cấp
        if role == 'DOCTOR':
            from users.models import DoctorProfile
            from users.serializers import DoctorProfileSerializer

            # Lấy dữ liệu profile từ request hoặc tạo dict trống
            profile_data = data.get('doctor_profile', {})
            # Thêm user vào profile_data
            profile_data['user'] = user.id

            # Thiết lập các trường bắt buộc nếu chưa có
            if not profile_data.get('specialization'):
                profile_data['specialization'] = 'GENERAL_PRACTICE'
            if not profile_data.get('license_number'):
                import random
                import string
                profile_data['license_number'] = 'DR' + ''.join(random.choices(string.digits, k=6))
            if not profile_data.get('years_of_experience'):
                profile_data['years_of_experience'] = 0
            if not profile_data.get('department'):
                profile_data['department'] = 'General'
            # consultation_fee không còn là trường bắt buộc
            if not profile_data.get('working_days'):
                profile_data['working_days'] = 'MON,TUE,WED,THU,FRI'
            if not profile_data.get('working_hours'):
                profile_data['working_hours'] = '08:00-17:00'

            # Kiểm tra và tạo profile
            profile_serializer = DoctorProfileSerializer(data=profile_data)
            if profile_serializer.is_valid():
                profile = profile_serializer.save()
            else:
                # Nếu dữ liệu profile không hợp lệ, tạo profile với các giá trị mặc định
                DoctorProfile.objects.create(
                    user=user,
                    specialization='GENERAL_PRACTICE',
                    license_number='DR' + ''.join(random.choices(string.digits, k=6)),
                    years_of_experience=0,
                    department='General',

                    working_days='MON,TUE,WED,THU,FRI',
                    working_hours='08:00-17:00'
                )

        elif role == 'NURSE':
            from users.models import NurseProfile
            from users.serializers import NurseProfileSerializer

            # Lấy dữ liệu profile từ request hoặc tạo dict trống
            profile_data = data.get('nurse_profile', {})
            # Thêm user vào profile_data
            profile_data['user'] = user.id

            # Thiết lập các trường bắt buộc nếu chưa có
            if not profile_data.get('license_number'):
                import random
                import string
                profile_data['license_number'] = 'NR' + ''.join(random.choices(string.digits, k=6))
            if not profile_data.get('nurse_type'):
                profile_data['nurse_type'] = 'RN'
            if not profile_data.get('department'):
                profile_data['department'] = 'GENERAL'

            # Kiểm tra và tạo profile
            profile_serializer = NurseProfileSerializer(data=profile_data)
            if profile_serializer.is_valid():
                profile = profile_serializer.save()
            else:
                # Nếu dữ liệu profile không hợp lệ, tạo profile với các giá trị mặc định
                NurseProfile.objects.create(
                    user=user,
                    license_number='NR' + ''.join(random.choices(string.digits, k=6)),
                    nurse_type='RN',
                    department='GENERAL'
                )

        elif role == 'PHARMACIST':
            from users.models import PharmacistProfile
            from users.serializers import PharmacistProfileSerializer

            # Lấy dữ liệu profile từ request hoặc tạo dict trống
            profile_data = data.get('pharmacist_profile', {})
            # Thêm user vào profile_data
            profile_data['user'] = user.id

            # Thiết lập các trường bắt buộc nếu chưa có
            if not profile_data.get('license_number'):
                import random
                import string
                profile_data['license_number'] = 'PH' + ''.join(random.choices(string.digits, k=6))
            if not profile_data.get('specialization'):
                profile_data['specialization'] = 'RETAIL'
            if not profile_data.get('pharmacy_name'):
                profile_data['pharmacy_name'] = 'General Pharmacy'

            # Kiểm tra và tạo profile
            profile_serializer = PharmacistProfileSerializer(data=profile_data)
            if profile_serializer.is_valid():
                profile = profile_serializer.save()
            else:
                # Nếu dữ liệu profile không hợp lệ, tạo profile với các giá trị mặc định
                PharmacistProfile.objects.create(
                    user=user,
                    license_number='PH' + ''.join(random.choices(string.digits, k=6)),
                    specialization='RETAIL',
                    pharmacy_name='General Pharmacy'
                )

        elif role == 'LAB_TECH':
            from users.models import LabTechnicianProfile
            from users.serializers import LabTechnicianProfileSerializer

            # Lấy dữ liệu profile từ request hoặc tạo dict trống
            profile_data = data.get('lab_technician_profile', {})
            # Thêm user vào profile_data
            profile_data['user'] = user.id

            # Thiết lập các trường bắt buộc nếu chưa có
            if not profile_data.get('license_number'):
                import random
                import string
                profile_data['license_number'] = 'LT' + ''.join(random.choices(string.digits, k=6))
            if not profile_data.get('specialization'):
                profile_data['specialization'] = 'GENERAL'
            if not profile_data.get('laboratory_name'):
                profile_data['laboratory_name'] = 'General Laboratory'

            # Kiểm tra và tạo profile
            profile_serializer = LabTechnicianProfileSerializer(data=profile_data)
            if profile_serializer.is_valid():
                profile = profile_serializer.save()
            else:
                # Nếu dữ liệu profile không hợp lệ, tạo profile với các giá trị mặc định
                LabTechnicianProfile.objects.create(
                    user=user,
                    license_number='LT' + ''.join(random.choices(string.digits, k=6)),
                    specialization='GENERAL',
                    laboratory_name='General Laboratory'
                )

        elif role == 'INSURANCE':
            from users.models import InsuranceProviderProfile
            from users.serializers import InsuranceProviderProfileSerializer

            # Lấy dữ liệu profile từ request hoặc tạo dict trống
            profile_data = data.get('insurance_provider_profile', {})
            # Thêm user vào profile_data
            profile_data['user'] = user.id

            # Thiết lập các trường bắt buộc nếu chưa có
            if not profile_data.get('company_name'):
                profile_data['company_name'] = 'General Insurance'
            if not profile_data.get('provider_id'):
                import random
                import string
                profile_data['provider_id'] = 'INS' + ''.join(random.choices(string.digits, k=6))
            if not profile_data.get('contact_person'):
                profile_data['contact_person'] = f"{user.first_name} {user.last_name}"
            if not profile_data.get('contact_email'):
                profile_data['contact_email'] = user.email
            if not profile_data.get('contact_phone'):
                profile_data['contact_phone'] = '0123456789'
            if not profile_data.get('service_areas'):
                profile_data['service_areas'] = 'All Areas'
            if not profile_data.get('available_plans'):
                profile_data['available_plans'] = 'Basic, Standard, Premium'

            # Kiểm tra và tạo profile
            profile_serializer = InsuranceProviderProfileSerializer(data=profile_data)
            if profile_serializer.is_valid():
                profile = profile_serializer.save()
            else:
                # Nếu dữ liệu profile không hợp lệ, tạo profile với các giá trị mặc định
                InsuranceProviderProfile.objects.create(
                    user=user,
                    company_name='General Insurance',
                    provider_id='INS' + ''.join(random.choices(string.digits, k=6)),
                    contact_person=f"{user.first_name} {user.last_name}",
                    contact_email=user.email,
                    contact_phone='0123456789',
                    service_areas='All Areas',
                    available_plans='Basic, Standard, Premium'
                )

        elif role == 'ADMIN':
            from users.models import AdminProfile
            from users.serializers import AdminProfileSerializer

            # Lấy dữ liệu profile từ request hoặc tạo dict trống
            profile_data = data.get('admin_profile', {})
            # Thêm user vào profile_data
            profile_data['user'] = user.id

            # Thiết lập các trường bắt buộc nếu chưa có
            if not profile_data.get('admin_type'):
                profile_data['admin_type'] = 'HOSPITAL'
            if not profile_data.get('employee_id'):
                import random
                import string
                profile_data['employee_id'] = 'ADM' + ''.join(random.choices(string.digits, k=6))
            if not profile_data.get('position'):
                profile_data['position'] = 'System Administrator'
            if not profile_data.get('access_level'):
                profile_data['access_level'] = 3

            # Kiểm tra và tạo profile
            profile_serializer = AdminProfileSerializer(data=profile_data)
            if profile_serializer.is_valid():
                profile = profile_serializer.save()
            else:
                # Nếu dữ liệu profile không hợp lệ, tạo profile với các giá trị mặc định
                AdminProfile.objects.create(
                    user=user,
                    admin_type='HOSPITAL',
                    employee_id='ADM' + ''.join(random.choices(string.digits, k=6)),
                    position='System Administrator',
                    access_level=3
                )

        # Trả về thông tin người dùng đã tạo
        serializer = UserDetailSerializer(user)
        return Response({
            "user": serializer.data,
            "password": data.get('password')  # Trả về mật khẩu nếu được tạo tự động
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ============================================================
# Doctors API
# ============================================================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_doctors(request):
    """
    API endpoint để lấy danh sách bác sĩ.
    Tất cả người dùng đã xác thực đều có thể truy cập endpoint này.
    """
    # Lấy danh sách người dùng có vai trò DOCTOR
    doctors = User.objects.filter(role='DOCTOR', is_active=True)

    # Lọc theo chuyên khoa nếu có
    specialty = request.query_params.get('specialty')
    if specialty:
        doctors = doctors.filter(doctor_profile__specialization=specialty)

    # Tìm kiếm theo tên nếu có
    search = request.query_params.get('search')
    if search:
        doctors = doctors.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )

    # Sử dụng serializer để trả về dữ liệu
    serializer = UserDetailSerializer(doctors, many=True)
    return Response(serializer.data)

# ============================================================
# Specialties API
# ============================================================

@api_view(['GET'])
def specialties(request):
    """
    API endpoint for getting specialties.
    """
    # Xác thực người dùng
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    # Lấy tham số department nếu có
    department = request.query_params.get('department', None)

    # Lấy danh sách chuyên khoa từ model DoctorProfile
    specialties = []
    for choice in DoctorProfile.SPECIALIZATION_CHOICES:
        specialty_id = choice[0]

        # Nếu có tham số department, chỉ trả về các chuyên khoa thuộc khoa đó
        if department:
            # Kiểm tra xem chuyên khoa có thuộc khoa được chọn không
            if department == 'KHOA_NOI' and specialty_id.startswith('NOI_'):
                specialties.append({
                    'id': specialty_id,
                    'name': choice[1],
                    'description': _get_description_for_specialty(specialty_id),
                    'department': department
                })
            elif department == 'KHOA_NGOAI' and specialty_id.startswith('NGOAI_'):
                specialties.append({
                    'id': specialty_id,
                    'name': choice[1],
                    'description': _get_description_for_specialty(specialty_id),
                    'department': department
                })
            elif department == 'KHOA_SAN' and (specialty_id.startswith('SAN_') or specialty_id.startswith('PHU_') or specialty_id == 'VO_SINH'):
                specialties.append({
                    'id': specialty_id,
                    'name': choice[1],
                    'description': _get_description_for_specialty(specialty_id),
                    'department': department
                })
            elif department == 'KHOA_NHI' and specialty_id.startswith('NHI_'):
                specialties.append({
                    'id': specialty_id,
                    'name': choice[1],
                    'description': _get_description_for_specialty(specialty_id),
                    'department': department
                })
            elif department == 'KHOA_MAT' and specialty_id == 'MAT':
                specialties.append({
                    'id': specialty_id,
                    'name': choice[1],
                    'description': _get_description_for_specialty(specialty_id),
                    'department': department
                })
            elif department == 'KHOA_TMH' and specialty_id == 'TAI_MUI_HONG':
                specialties.append({
                    'id': specialty_id,
                    'name': choice[1],
                    'description': _get_description_for_specialty(specialty_id),
                    'department': department
                })
            elif department == 'KHOA_RHM' and specialty_id == 'RANG_HAM_MAT':
                specialties.append({
                    'id': specialty_id,
                    'name': choice[1],
                    'description': _get_description_for_specialty(specialty_id),
                    'department': department
                })
            elif department == 'KHOA_UNG_BUOU' and specialty_id == 'UNG_BUOU':
                specialties.append({
                    'id': specialty_id,
                    'name': choice[1],
                    'description': _get_description_for_specialty(specialty_id),
                    'department': department
                })
        else:
            # Nếu không có tham số department, trả về tất cả chuyên khoa
            # Xác định khoa cho chuyên khoa
            department_id = None
            if specialty_id.startswith('NOI_'):
                department_id = 'KHOA_NOI'
            elif specialty_id.startswith('NGOAI_'):
                department_id = 'KHOA_NGOAI'
            elif specialty_id.startswith('SAN_') or specialty_id.startswith('PHU_') or specialty_id == 'VO_SINH':
                department_id = 'KHOA_SAN'
            elif specialty_id.startswith('NHI_'):
                department_id = 'KHOA_NHI'
            elif specialty_id == 'MAT':
                department_id = 'KHOA_MAT'
            elif specialty_id == 'TAI_MUI_HONG':
                department_id = 'KHOA_TMH'
            elif specialty_id == 'RANG_HAM_MAT':
                department_id = 'KHOA_RHM'
            elif specialty_id == 'UNG_BUOU':
                department_id = 'KHOA_UNG_BUOU'

            specialties.append({
                'id': specialty_id,
                'name': choice[1],
                'description': _get_description_for_specialty(specialty_id),
                'department': department_id
            })

    return Response(specialties)

@api_view(['GET'])
def departments(request):
    """
    API endpoint for getting departments.
    """
    # Xác thực người dùng
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    # Lấy danh sách khoa từ model NurseProfile
    departments = []
    for choice in NurseProfile.DEPARTMENT_CHOICES:
        department_id = choice[0]

        # Đếm số lượng chuyên khoa thuộc khoa này
        specialty_count = 0
        specialties = []

        for specialty in DoctorProfile.SPECIALIZATION_CHOICES:
            specialty_id = specialty[0]

            # Kiểm tra xem chuyên khoa có thuộc khoa này không
            if department_id == 'KHOA_NOI' and specialty_id.startswith('NOI_'):
                specialty_count += 1
                specialties.append(specialty_id)
            elif department_id == 'KHOA_NGOAI' and specialty_id.startswith('NGOAI_'):
                specialty_count += 1
                specialties.append(specialty_id)
            elif department_id == 'KHOA_SAN' and (specialty_id.startswith('SAN_') or specialty_id.startswith('PHU_') or specialty_id == 'VO_SINH'):
                specialty_count += 1
                specialties.append(specialty_id)
            elif department_id == 'KHOA_NHI' and specialty_id.startswith('NHI_'):
                specialty_count += 1
                specialties.append(specialty_id)
            elif department_id == 'KHOA_MAT' and specialty_id == 'MAT':
                specialty_count += 1
                specialties.append(specialty_id)
            elif department_id == 'KHOA_TMH' and specialty_id == 'TAI_MUI_HONG':
                specialty_count += 1
                specialties.append(specialty_id)
            elif department_id == 'KHOA_RHM' and specialty_id == 'RANG_HAM_MAT':
                specialty_count += 1
                specialties.append(specialty_id)
            elif department_id == 'KHOA_UNG_BUOU' and specialty_id == 'UNG_BUOU':
                specialty_count += 1
                specialties.append(specialty_id)

        departments.append({
            'id': department_id,
            'name': choice[1],
            'description': _get_description_for_department(department_id),
            'specialty_count': specialty_count,
            'specialties': specialties
        })

    return Response(departments)

def _get_description_for_department(department):
    """
    Get description for department.
    """
    descriptions = {
        'KHOA_NOI': 'Khoa chịu trách nhiệm chẩn đoán và điều trị các bệnh nội khoa',
        'KHOA_NGOAI': 'Khoa chịu trách nhiệm phẫu thuật và điều trị các bệnh ngoại khoa',
        'KHOA_SAN': 'Khoa chăm sóc sức khỏe phụ nữ và thai sản',
        'KHOA_NHI': 'Khoa chăm sóc sức khỏe trẻ em từ sơ sinh đến 16 tuổi',
        'KHOA_CAP_CUU': 'Khoa tiếp nhận và xử lý các trường hợp cấp cứu',
        'KHOA_XET_NGHIEM': 'Khoa thực hiện các xét nghiệm và phân tích mẫu',
        'KHOA_CHAN_DOAN_HINH_ANH': 'Khoa thực hiện các kỹ thuật chẩn đoán hình ảnh như X-quang, CT, MRI',
        'KHOA_MAT': 'Khoa chuyên về chăm sóc và điều trị các vấn đề về mắt',
        'KHOA_TMH': 'Khoa chuyên về chăm sóc và điều trị các vấn đề về tai, mũi, họng',
        'KHOA_RHM': 'Khoa chuyên về chăm sóc và điều trị các vấn đề về răng, hàm, mặt',
        'KHOA_UNG_BUOU': 'Khoa chuyên về chẩn đoán và điều trị các loại ung thư',
        'KHOA_HOI_SUC': 'Khoa chăm sóc đặc biệt cho bệnh nhân nặng',
        'KHOA_KHAC': 'Các khoa khác trong bệnh viện'
    }
    return descriptions.get(department, '')

# ============================================================
# Insurance Information API
# ============================================================

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def list_insurance_information(request):
    """
    API endpoint để lấy danh sách hoặc tạo thông tin bảo hiểm.
    Lọc theo patient_id nếu được cung cấp.
    """
    # Xử lý GET request
    if request.method == 'GET':
        # Kiểm tra quyền truy cập
        user = request.user
        patient_id = request.query_params.get('patient_id')

        # Nếu không phải ADMIN, INSURANCE hoặc DOCTOR, chỉ cho phép xem thông tin bảo hiểm của chính mình
        if user.role not in ['ADMIN', 'INSURANCE', 'DOCTOR'] and str(user.id) != patient_id:
            return Response(
                {"detail": "You do not have permission to view this insurance information."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Lọc theo patient_id nếu được cung cấp
        if patient_id:
            # Lấy hồ sơ bệnh nhân
            try:
                patient_profile = PatientProfile.objects.get(user_id=patient_id)
            except PatientProfile.DoesNotExist:
                return Response(
                    {"detail": "Patient profile not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Lấy thông tin bảo hiểm từ hồ sơ bệnh nhân
            insurance_info = InsuranceInformation.objects.filter(id=patient_profile.insurance_information_id) if patient_profile.insurance_information_id else []
        else:
            # Nếu không có patient_id, trả về tất cả thông tin bảo hiểm (chỉ cho ADMIN và INSURANCE)
            if user.role not in ['ADMIN', 'INSURANCE']:
                return Response(
                    {"detail": "You must provide a patient_id."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            insurance_info = InsuranceInformation.objects.all()

        # Serialize dữ liệu
        serializer = InsuranceInformationSerializer(insurance_info, many=True)

        # Trả về kết quả
        return Response({
            "count": len(serializer.data),
            "next": None,
            "previous": None,
            "results": serializer.data
        })

    # Xử lý POST request
    elif request.method == 'POST':
        # Kiểm tra quyền truy cập
        if request.user.role not in ['ADMIN', 'INSURANCE']:
            return Response(
                {"detail": "Only administrators and insurance providers can create insurance information."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Tạo thông tin bảo hiểm mới
        serializer = InsuranceInformationSerializer(data=request.data)
        if serializer.is_valid():
            insurance_info = serializer.save()

            # Cập nhật hồ sơ bệnh nhân nếu có patient_id
            patient_id = request.data.get('patient_id')
            if patient_id:
                try:
                    patient_profile = PatientProfile.objects.get(user_id=patient_id)
                    patient_profile.insurance_information = insurance_info
                    patient_profile.save()
                except PatientProfile.DoesNotExist:
                    pass  # Không cập nhật nếu không tìm thấy hồ sơ bệnh nhân

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def _get_description_for_specialty(specialty):
    """
    Get description for specialty.
    """
    descriptions = {
        # Chuyên khoa thuộc Khoa Nội
        'NOI_TIM_MACH': 'Chuyên khoa về chẩn đoán và điều trị các bệnh lý tim mạch',
        'NOI_TIEU_HOA': 'Chuyên khoa về chẩn đoán và điều trị các bệnh lý đường tiêu hóa',
        'NOI_HO_HAP': 'Chuyên khoa về chẩn đoán và điều trị các bệnh lý hô hấp',
        'NOI_THAN': 'Chuyên khoa về chẩn đoán và điều trị các bệnh lý thận và tiết niệu',
        'NOI_TIET': 'Chuyên khoa về chẩn đoán và điều trị các bệnh lý nội tiết',
        'NOI_THAN_KINH': 'Chuyên khoa về chẩn đoán và điều trị các bệnh lý thần kinh',
        'NOI_DA_LIEU': 'Chuyên khoa về chẩn đoán và điều trị các bệnh lý da liễu',
        'NOI_TONG_QUAT': 'Chuyên khoa về chẩn đoán và điều trị các bệnh nội khoa tổng quát',

        # Chuyên khoa thuộc Khoa Ngoại
        'NGOAI_CHINH_HINH': 'Chuyên khoa về chấn thương và chỉnh hình xương khớp',
        'NGOAI_TIET_NIEU': 'Chuyên khoa về phẫu thuật và điều trị các bệnh lý tiết niệu',
        'NGOAI_THAN_KINH': 'Chuyên khoa về phẫu thuật và điều trị các bệnh lý thần kinh',
        'NGOAI_LONG_NGUC': 'Chuyên khoa về phẫu thuật và điều trị các bệnh lý lồng ngực và mạch máu',
        'NGOAI_TIEU_HOA': 'Chuyên khoa về phẫu thuật và điều trị các bệnh lý tiêu hóa',
        'NGOAI_TONG_QUAT': 'Chuyên khoa về phẫu thuật và điều trị các bệnh ngoại khoa tổng quát',

        # Chuyên khoa thuộc Khoa Sản - Phụ khoa
        'SAN_KHOA': 'Chuyên khoa về chăm sóc thai sản và đứa trẻ sơ sinh',
        'PHU_KHOA': 'Chuyên khoa về chẩn đoán và điều trị các bệnh lý phụ khoa',
        'VO_SINH': 'Chuyên khoa về chẩn đoán và điều trị vô sinh và hiếm muộn',

        # Chuyên khoa thuộc Khoa Nhi
        'NHI_TONG_QUAT': 'Chuyên khoa về chăm sóc sức khỏe trẻ em tổng quát',
        'NHI_TIM_MACH': 'Chuyên khoa về chẩn đoán và điều trị các bệnh lý tim mạch ở trẻ em',
        'NHI_THAN_KINH': 'Chuyên khoa về chẩn đoán và điều trị các bệnh lý thần kinh ở trẻ em',
        'NHI_SO_SINH': 'Chuyên khoa về chăm sóc trẻ sơ sinh và trẻ sinh non',

        # Các chuyên khoa khác
        'MAT': 'Chuyên khoa về chẩn đoán và điều trị các bệnh lý về mắt',
        'TAI_MUI_HONG': 'Chuyên khoa về chẩn đoán và điều trị các bệnh lý về tai, mũi, họng',
        'RANG_HAM_MAT': 'Chuyên khoa về chẩn đoán và điều trị các bệnh lý về răng, hàm, mặt',
        'TAM_THAN': 'Chuyên khoa về chẩn đoán và điều trị các bệnh lý tâm thần',
        'UNG_BUOU': 'Chuyên khoa về chẩn đoán và điều trị các loại ung thư',
        'DA_KHOA': 'Chuyên khoa về chẩn đoán và điều trị nhiều loại bệnh khác nhau',
        'KHAC': 'Các chuyên khoa khác'
    }
    return descriptions.get(specialty, '')

# ============================================================
# Nurse Profile APIs
# ============================================================

class NurseProfileAPI(APIView):
    """
    API endpoint để quản lý hồ sơ y tá.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Lấy hồ sơ y tá của người dùng hiện tại"""
        try:
            profile = NurseProfile.objects.get(user=request.user)
            serializer = NurseProfileSerializer(profile)
            return Response(serializer.data)
        except NurseProfile.DoesNotExist:
            return Response({"detail": "Nurse profile not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """Tạo hồ sơ y tá mới cho người dùng hiện tại"""
        # Kiểm tra vai trò người dùng
        if request.user.role != 'NURSE':
            return Response(
                {"detail": "Only users with NURSE role can create nurse profiles."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Kiểm tra xem người dùng đã có hồ sơ y tá chưa
        if NurseProfile.objects.filter(user=request.user).exists():
            return Response(
                {"detail": "User already has a nurse profile. Use PUT to update."},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = request.data.copy()
        data['user'] = request.user.id

        serializer = NurseProfileSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """Cập nhật hồ sơ y tá của người dùng hiện tại"""
        try:
            profile = NurseProfile.objects.get(user=request.user)
            serializer = NurseProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except NurseProfile.DoesNotExist:
            return Response(
                {"detail": "Nurse profile not found. Use POST to create."},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request):
        """Xóa hồ sơ y tá của người dùng hiện tại"""
        try:
            profile = NurseProfile.objects.get(user=request.user)
            profile.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except NurseProfile.DoesNotExist:
            return Response({"detail": "Nurse profile not found."}, status=status.HTTP_404_NOT_FOUND)


# ============================================================
# User Preference APIs
# ============================================================

class UserPreferenceAPI(APIView):
    """
    API endpoint để quản lý tùy chọn của người dùng.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Lấy tùy chọn của người dùng hiện tại"""
        try:
            preference = UserPreference.objects.get(user=request.user)
            serializer = UserPreferenceSerializer(preference)
            return Response(serializer.data)
        except UserPreference.DoesNotExist:
            # Tạo tùy chọn mặc định nếu chưa có
            preference = UserPreference.objects.create(user=request.user)
            serializer = UserPreferenceSerializer(preference)
            return Response(serializer.data)

    def put(self, request):
        """Cập nhật tùy chọn của người dùng hiện tại"""
        try:
            preference = UserPreference.objects.get(user=request.user)
        except UserPreference.DoesNotExist:
            preference = UserPreference.objects.create(user=request.user)

        serializer = UserPreferenceSerializer(preference, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ============================================================
# User Activity APIs
# ============================================================

class UserActivityListAPI(APIView):
    """
    API endpoint để lấy danh sách hoạt động của người dùng.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Lấy danh sách hoạt động của người dùng"""
        if request.user.role == 'ADMIN':
            # Admin có thể xem tất cả hoặc lọc theo người dùng
            user_id = request.query_params.get('user_id')
            if user_id:
                activities = UserActivity.objects.filter(user_id=user_id)
            else:
                activities = UserActivity.objects.all()
        else:
            # Người dùng thường chỉ xem hoạt động của mình
            activities = UserActivity.objects.filter(user=request.user)

        # Lọc theo loại hoạt động
        activity_type = request.query_params.get('activity_type')
        if activity_type:
            activities = activities.filter(activity_type=activity_type)

        # Lọc theo khoảng thời gian
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            activities = activities.filter(created_at__gte=start_date)
        if end_date:
            activities = activities.filter(created_at__lte=end_date)

        # Phân trang
        page_size = int(request.query_params.get('page_size', 20))
        page = int(request.query_params.get('page', 1))
        start = (page - 1) * page_size
        end = start + page_size

        activities = activities.order_by('-created_at')[start:end]
        serializer = UserActivitySerializer(activities, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Ghi lại hoạt động mới (chỉ dành cho hệ thống hoặc admin)"""
        if request.user.role != 'ADMIN':
            return Response(
                {"detail": "Only administrators can manually record activities."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = UserActivitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ============================================================
# User Session APIs
# ============================================================

class UserSessionListAPI(APIView):
    """
    API endpoint để lấy danh sách phiên làm việc của người dùng.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Lấy danh sách phiên làm việc của người dùng"""
        if request.user.role == 'ADMIN':
            # Admin có thể xem tất cả hoặc lọc theo người dùng
            user_id = request.query_params.get('user_id')
            if user_id:
                sessions = UserSession.objects.filter(user_id=user_id)
            else:
                sessions = UserSession.objects.all()
        else:
            # Người dùng thường chỉ xem phiên làm việc của mình
            sessions = UserSession.objects.filter(user=request.user)

        # Lọc theo trạng thái
        is_active = request.query_params.get('is_active')
        if is_active is not None:
            is_active = is_active.lower() == 'true'
            sessions = sessions.filter(is_active=is_active)

        # Lọc theo khoảng thời gian
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            sessions = sessions.filter(created_at__gte=start_date)
        if end_date:
            sessions = sessions.filter(created_at__lte=end_date)

        sessions = sessions.order_by('-created_at')
        serializer = UserSessionSerializer(sessions, many=True)
        return Response(serializer.data)

class UserSessionDetailAPI(APIView):
    """
    API endpoint để quản lý phiên làm việc cụ thể.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        """Lấy đối tượng phiên làm việc dựa trên ID"""
        try:
            session = UserSession.objects.get(pk=pk)
            # Kiểm tra quyền truy cập
            if session.user.id != self.request.user.id and self.request.user.role != 'ADMIN':
                raise ValidationError({"detail": "You do not have permission to access this session."})
            return session
        except UserSession.DoesNotExist:
            raise ValidationError({"detail": "Session not found."})

    def get(self, request, pk):
        """Lấy thông tin chi tiết của phiên làm việc"""
        session = self.get_object(pk)
        serializer = UserSessionSerializer(session)
        return Response(serializer.data)

    def delete(self, request, pk):
        """Vô hiệu hóa phiên làm việc (logout)"""
        session = self.get_object(pk)
        session.invalidate()
        return Response({"detail": "Session invalidated successfully."}, status=status.HTTP_200_OK)

# ============================================================
# Pharmacist Profile APIs
# ============================================================

class PharmacistProfileAPI(APIView):
    """
    API endpoint để quản lý hồ sơ dược sĩ.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Lấy hồ sơ dược sĩ của người dùng hiện tại"""
        try:
            profile = PharmacistProfile.objects.get(user=request.user)
            serializer = PharmacistProfileSerializer(profile)
            return Response(serializer.data)
        except PharmacistProfile.DoesNotExist:
            return Response({"detail": "Pharmacist profile not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """Tạo hồ sơ dược sĩ mới cho người dùng hiện tại"""
        # Kiểm tra vai trò người dùng
        if request.user.role != 'PHARMACIST':
            return Response(
                {"detail": "Only users with PHARMACIST role can create pharmacist profiles."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Kiểm tra xem người dùng đã có hồ sơ dược sĩ chưa
        if PharmacistProfile.objects.filter(user=request.user).exists():
            return Response(
                {"detail": "User already has a pharmacist profile. Use PUT to update."},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = request.data.copy()
        data['user'] = request.user.id

        serializer = PharmacistProfileSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """Cập nhật hồ sơ dược sĩ của người dùng hiện tại"""
        try:
            profile = PharmacistProfile.objects.get(user=request.user)
            serializer = PharmacistProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except PharmacistProfile.DoesNotExist:
            return Response(
                {"detail": "Pharmacist profile not found. Use POST to create."},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request):
        """Xóa hồ sơ dược sĩ của người dùng hiện tại"""
        try:
            profile = PharmacistProfile.objects.get(user=request.user)
            profile.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except PharmacistProfile.DoesNotExist:
            return Response({"detail": "Pharmacist profile not found."}, status=status.HTTP_404_NOT_FOUND)

# ============================================================
# Insurance Provider Profile APIs
# ============================================================

class InsuranceProviderProfileAPI(APIView):
    """
    API endpoint để quản lý hồ sơ nhà cung cấp bảo hiểm.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Lấy hồ sơ nhà cung cấp bảo hiểm của người dùng hiện tại"""
        try:
            profile = InsuranceProviderProfile.objects.get(user=request.user)
            serializer = InsuranceProviderProfileSerializer(profile)
            return Response(serializer.data)
        except InsuranceProviderProfile.DoesNotExist:
            return Response({"detail": "Insurance provider profile not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """Tạo hồ sơ nhà cung cấp bảo hiểm mới cho người dùng hiện tại"""
        # Kiểm tra vai trò người dùng
        if request.user.role != 'INSURANCE':
            return Response(
                {"detail": "Only users with INSURANCE role can create insurance provider profiles."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Kiểm tra xem người dùng đã có hồ sơ nhà cung cấp bảo hiểm chưa
        if InsuranceProviderProfile.objects.filter(user=request.user).exists():
            return Response(
                {"detail": "User already has an insurance provider profile. Use PUT to update."},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = request.data.copy()
        data['user'] = request.user.id

        serializer = InsuranceProviderProfileSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """Cập nhật hồ sơ nhà cung cấp bảo hiểm của người dùng hiện tại"""
        try:
            profile = InsuranceProviderProfile.objects.get(user=request.user)
            serializer = InsuranceProviderProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except InsuranceProviderProfile.DoesNotExist:
            return Response(
                {"detail": "Insurance provider profile not found. Use POST to create."},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request):
        """Xóa hồ sơ nhà cung cấp bảo hiểm của người dùng hiện tại"""
        try:
            profile = InsuranceProviderProfile.objects.get(user=request.user)
            profile.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except InsuranceProviderProfile.DoesNotExist:
            return Response({"detail": "Insurance provider profile not found."}, status=status.HTTP_404_NOT_FOUND)

# ============================================================
# Lab Technician Profile APIs
# ============================================================

class LabTechnicianProfileAPI(APIView):
    """
    API endpoint để quản lý hồ sơ kỹ thuật viên phòng thí nghiệm.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Lấy hồ sơ kỹ thuật viên phòng thí nghiệm của người dùng hiện tại"""
        try:
            profile = LabTechnicianProfile.objects.get(user=request.user)
            serializer = LabTechnicianProfileSerializer(profile)
            return Response(serializer.data)
        except LabTechnicianProfile.DoesNotExist:
            return Response({"detail": "Lab technician profile not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """Tạo hồ sơ kỹ thuật viên phòng thí nghiệm mới cho người dùng hiện tại"""
        # Kiểm tra vai trò người dùng
        if request.user.role != 'LAB_TECH':
            return Response(
                {"detail": "Only users with LAB_TECH role can create lab technician profiles."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Kiểm tra xem người dùng đã có hồ sơ kỹ thuật viên phòng thí nghiệm chưa
        if LabTechnicianProfile.objects.filter(user=request.user).exists():
            return Response(
                {"detail": "User already has a lab technician profile. Use PUT to update."},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = request.data.copy()
        data['user'] = request.user.id

        serializer = LabTechnicianProfileSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """Cập nhật hồ sơ kỹ thuật viên phòng thí nghiệm của người dùng hiện tại"""
        try:
            profile = LabTechnicianProfile.objects.get(user=request.user)
            serializer = LabTechnicianProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except LabTechnicianProfile.DoesNotExist:
            return Response(
                {"detail": "Lab technician profile not found. Use POST to create."},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request):
        """Xóa hồ sơ kỹ thuật viên phòng thí nghiệm của người dùng hiện tại"""
        try:
            profile = LabTechnicianProfile.objects.get(user=request.user)
            profile.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except LabTechnicianProfile.DoesNotExist:
            return Response({"detail": "Lab technician profile not found."}, status=status.HTTP_404_NOT_FOUND)

# ============================================================
# Admin Profile APIs
# ============================================================

class AdminProfileAPI(APIView):
    """
    API endpoint để quản lý hồ sơ quản trị viên.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Lấy hồ sơ quản trị viên của người dùng hiện tại"""
        try:
            profile = AdminProfile.objects.get(user=request.user)
            serializer = AdminProfileSerializer(profile)
            return Response(serializer.data)
        except AdminProfile.DoesNotExist:
            return Response({"detail": "Admin profile not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """Tạo hồ sơ quản trị viên mới cho người dùng hiện tại"""
        # Kiểm tra vai trò người dùng
        if request.user.role != 'ADMIN':
            return Response(
                {"detail": "Only users with ADMIN role can create admin profiles."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Kiểm tra xem người dùng đã có hồ sơ quản trị viên chưa
        if AdminProfile.objects.filter(user=request.user).exists():
            return Response(
                {"detail": "User already has an admin profile. Use PUT to update."},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = request.data.copy()
        data['user'] = request.user.id

        serializer = AdminProfileSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """Cập nhật hồ sơ quản trị viên của người dùng hiện tại"""
        try:
            profile = AdminProfile.objects.get(user=request.user)
            serializer = AdminProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except AdminProfile.DoesNotExist:
            return Response(
                {"detail": "Admin profile not found. Use POST to create."},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request):
        """Xóa hồ sơ quản trị viên của người dùng hiện tại"""
        try:
            profile = AdminProfile.objects.get(user=request.user)
            profile.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except AdminProfile.DoesNotExist:
            return Response({"detail": "Admin profile not found."}, status=status.HTTP_404_NOT_FOUND)

# ============================================================
# Admin APIs for listing all profiles
# ============================================================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_all_patient_profiles(request):
    """API endpoint để admin xem tất cả hồ sơ bệnh nhân."""
    if request.user.role != 'ADMIN':
        return Response(
            {"detail": "Only administrators can access this endpoint."},
            status=status.HTTP_403_FORBIDDEN
        )

    profiles = PatientProfile.objects.all()
    serializer = PatientProfileSerializer(profiles, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_all_doctor_profiles(request):
    """API endpoint để admin xem tất cả hồ sơ bác sĩ."""
    if request.user.role != 'ADMIN':
        return Response(
            {"detail": "Only administrators can access this endpoint."},
            status=status.HTTP_403_FORBIDDEN
        )

    profiles = DoctorProfile.objects.all()
    serializer = DoctorProfileSerializer(profiles, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_all_nurse_profiles(request):
    """API endpoint để admin xem tất cả hồ sơ y tá."""
    if request.user.role != 'ADMIN':
        return Response(
            {"detail": "Only administrators can access this endpoint."},
            status=status.HTTP_403_FORBIDDEN
        )

    profiles = NurseProfile.objects.all()
    serializer = NurseProfileSerializer(profiles, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_all_pharmacist_profiles(request):
    """API endpoint để admin xem tất cả hồ sơ dược sĩ."""
    if request.user.role != 'ADMIN':
        return Response(
            {"detail": "Only administrators can access this endpoint."},
            status=status.HTTP_403_FORBIDDEN
        )

    profiles = PharmacistProfile.objects.all()
    serializer = PharmacistProfileSerializer(profiles, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_all_insurance_provider_profiles(request):
    """API endpoint để admin xem tất cả hồ sơ nhà cung cấp bảo hiểm."""
    if request.user.role != 'ADMIN':
        return Response(
            {"detail": "Only administrators can access this endpoint."},
            status=status.HTTP_403_FORBIDDEN
        )

    profiles = InsuranceProviderProfile.objects.all()
    serializer = InsuranceProviderProfileSerializer(profiles, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_all_lab_technician_profiles(request):
    """API endpoint để admin xem tất cả hồ sơ kỹ thuật viên phòng thí nghiệm."""
    if request.user.role != 'ADMIN':
        return Response(
            {"detail": "Only administrators can access this endpoint."},
            status=status.HTTP_403_FORBIDDEN
        )

    profiles = LabTechnicianProfile.objects.all()
    serializer = LabTechnicianProfileSerializer(profiles, many=True)
    return Response(serializer.data)
