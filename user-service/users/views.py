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
            profile = PatientProfile.objects.get(user=request.user)
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
        if PatientProfile.objects.filter(user=request.user).exists():
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
            profile = PatientProfile.objects.get(user=request.user)
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
