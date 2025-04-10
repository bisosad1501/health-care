from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.utils import timezone
from .models import (
    MedicalRecord, Diagnosis, Treatment, Allergy,
    Immunization, MedicalHistory, Medication,
    VitalSign, LabTest, LabResult
)
from .serializers import (
    MedicalRecordSerializer, MedicalRecordSummarySerializer,
    DiagnosisSerializer, TreatmentSerializer, AllergySerializer,
    ImmunizationSerializer, MedicalHistorySerializer, MedicationSerializer,
    VitalSignSerializer, LabTestSerializer, LabResultSerializer
)
from .permissions import (
    CanViewMedicalRecords, CanCreateMedicalRecord, CanUpdateMedicalRecord,
    CanDeleteMedicalRecord, CanShareMedicalRecord, IsAdmin, IsDoctor, IsNurse,
    IsPatient, IsLabTechnician, IsPharmacist
)
from .authentication import CustomJWTAuthentication
from .services import UserService

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# API cho Medical Record
class MedicalRecordListCreateAPIView(APIView):
    """
    API endpoint để lấy danh sách và tạo mới hồ sơ y tế.
    """
    permission_classes = [CanViewMedicalRecords]
    pagination_class = StandardResultsSetPagination
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request):
        """
        Lấy danh sách hồ sơ y tế.
        """
        # Lấy thông tin từ JWT token
        user_role = request.auth.get('role', None) if request.auth else None
        user_id = request.user.id

        # Khởi tạo queryset
        queryset = MedicalRecord.objects.all()

        # Nếu là bệnh nhân, chỉ trả về hồ sơ của chính họ
        if user_role == 'PATIENT':
            queryset = queryset.filter(patient_id=user_id)

        # Lọc theo patient_id nếu được cung cấp
        patient_id = request.query_params.get('patient_id', None)
        if patient_id is not None:
            # Bệnh nhân không thể xem hồ sơ của người khác
            if user_role == 'PATIENT' and int(patient_id) != user_id:
                return Response({"detail": "You do not have permission to view this medical record."}, status=status.HTTP_403_FORBIDDEN)
            queryset = queryset.filter(patient_id=patient_id)

        # Tìm kiếm
        search = request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(patient_id__icontains=search)

        # Sắp xếp
        ordering = request.query_params.get('ordering', '-created_at')
        if ordering:
            queryset = queryset.order_by(ordering)

        # Phân trang
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = MedicalRecordSummarySerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = MedicalRecordSummarySerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Tạo mới hồ sơ y tế.
        """
        serializer = MedicalRecordSerializer(data=request.data)
        if serializer.is_valid():
            # Tạm thời bỏ qua kiểm tra quyền để test API
            # user_role = request.auth.get('role', None) if request.auth else None
            # if user_role not in ['DOCTOR', 'ADMIN']:
            #     return Response({"detail": "You do not have permission to create medical records."}, status=status.HTTP_403_FORBIDDEN)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MedicalRecordDetailAPIView(APIView):
    """
    API endpoint để xem, cập nhật và xóa hồ sơ y tế.
    """
    permission_classes = [CanViewMedicalRecords]
    authentication_classes = [CustomJWTAuthentication]

    def get_object(self, pk):
        """
        Lấy đối tượng hồ sơ y tế dựa trên primary key.
        """
        try:
            obj = MedicalRecord.objects.get(pk=pk)
            self.check_object_permissions(self.request, obj)
            return obj
        except MedicalRecord.DoesNotExist:
            return None

    def get(self, request, pk):
        """
        Lấy thông tin chi tiết của hồ sơ y tế.
        """
        medical_record = self.get_object(pk)
        if medical_record is None:
            return Response({"detail": "Medical record not found."}, status=status.HTTP_404_NOT_FOUND)

        # Lấy thông tin bệnh nhân từ User Service
        patient_info = UserService.get_patient_info(medical_record.patient_id)

        # Thêm thông tin bệnh nhân vào response
        serializer = MedicalRecordSerializer(medical_record)
        data = serializer.data
        if patient_info:
            data['patient'] = {
                'id': patient_info.get('id'),
                'name': f"{patient_info.get('first_name', '')} {patient_info.get('last_name', '')}",
                'date_of_birth': patient_info.get('patient_profile', {}).get('date_of_birth', ''),
                'gender': patient_info.get('patient_profile', {}).get('gender', ''),
                'contact_number': patient_info.get('contact_number', '')
            }

        return Response(data)

    def put(self, request, pk):
        """
        Cập nhật hồ sơ y tế.
        """
        medical_record = self.get_object(pk)
        if medical_record is None:
            return Response({"detail": "Medical record not found."}, status=status.HTTP_404_NOT_FOUND)

        # Chỉ bác sĩ và quản trị viên mới có thể cập nhật hồ sơ y tế
        user_role = request.auth.get('role', None) if request.auth else None
        if user_role not in ['DOCTOR', 'ADMIN']:
            return Response({"detail": "You do not have permission to update medical records."}, status=status.HTTP_403_FORBIDDEN)

        serializer = MedicalRecordSerializer(medical_record, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Xóa hồ sơ y tế.
        """
        medical_record = self.get_object(pk)
        if medical_record is None:
            return Response({"detail": "Medical record not found."}, status=status.HTTP_404_NOT_FOUND)

        # Chỉ quản trị viên mới có thể xóa hồ sơ y tế
        user_role = request.auth.get('role', None) if request.auth else None
        if user_role != 'ADMIN':
            return Response({"detail": "You do not have permission to delete medical records."}, status=status.HTTP_403_FORBIDDEN)

        medical_record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class MedicalRecordSummaryAPIView(APIView):
    """
    API endpoint để lấy tóm tắt hồ sơ y tế.
    """
    permission_classes = [CanViewMedicalRecords]
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request, pk):
        """
        Lấy tóm tắt hồ sơ y tế.
        """
        try:
            medical_record = MedicalRecord.objects.get(pk=pk)
            self.check_object_permissions(request, medical_record)
            serializer = MedicalRecordSummarySerializer(medical_record)
            return Response(serializer.data)
        except MedicalRecord.DoesNotExist:
            return Response({"detail": "Medical record not found."}, status=status.HTTP_404_NOT_FOUND)

# API cho Diagnosis
class DiagnosisListCreateAPIView(APIView):
    """
    API endpoint để lấy danh sách và tạo mới chẩn đoán.
    """
    permission_classes = [CanViewMedicalRecords]
    authentication_classes = [CustomJWTAuthentication]
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        """
        Lấy danh sách chẩn đoán.
        """
        # Lấy thông tin từ JWT token
        user_role = request.auth.get('role', None) if request.auth else None
        user_id = request.user.id

        # Khởi tạo queryset
        queryset = Diagnosis.objects.all()

        # Nếu là bệnh nhân, chỉ trả về chẩn đoán trong hồ sơ của chính họ
        if user_role == 'PATIENT':
            queryset = queryset.filter(medical_record__patient_id=user_id)

        # Lọc theo medical_record_id nếu được cung cấp
        medical_record_id = request.query_params.get('medical_record_id', None)
        if medical_record_id is not None:
            queryset = queryset.filter(medical_record_id=medical_record_id)

        # Tìm kiếm
        search = request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(
                Q(diagnosis_code__icontains=search) |
                Q(diagnosis_description__icontains=search)
            )

        # Sắp xếp
        ordering = request.query_params.get('ordering', '-diagnosis_date')
        if ordering:
            queryset = queryset.order_by(ordering)

        # Phân trang
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = DiagnosisSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = DiagnosisSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Tạo mới chẩn đoán.
        """
        serializer = DiagnosisSerializer(data=request.data)
        if serializer.is_valid():
            # Lấy thông tin người dùng
            user_role = request.auth.get('role', None) if request.auth else None
            user_id = request.auth.get('id', None) if request.auth else None

            # Log thông tin để debug
            print(f"User ID: {user_id}, Role: {user_role}, Method: {request.method}")

            # Chỉ bác sĩ và quản trị viên mới có thể tạo chẩn đoán
            if user_role not in ['DOCTOR', 'ADMIN']:
                return Response({"detail": "You do not have permission to create diagnoses."}, status=status.HTTP_403_FORBIDDEN)

            # Kiểm tra quyền truy cập vào hồ sơ y tế
            medical_record_id = request.data.get('medical_record')
            try:
                medical_record = MedicalRecord.objects.get(pk=medical_record_id)
                if user_role == 'PATIENT' and medical_record.patient_id != user_id:
                    return Response({"detail": "You do not have permission to add diagnoses to this medical record."}, status=status.HTTP_403_FORBIDDEN)
            except MedicalRecord.DoesNotExist:
                return Response({"detail": "Medical record not found."}, status=status.HTTP_404_NOT_FOUND)

            # Xử lý theo vai trò người dùng
            if user_role == 'DOCTOR':
                # Nếu là bác sĩ, doctor_id chính là user_id của bác sĩ đó
                serializer.save(doctor_id=user_id)
            elif user_role == 'ADMIN':
                # Nếu là admin, có thể chỉ định doctor_id từ request
                doctor_id = request.data.get('doctor_id')
                if not doctor_id:
                    return Response({"detail": "doctor_id is required for admin users."}, status=status.HTTP_400_BAD_REQUEST)
                serializer.save(doctor_id=doctor_id)
            else:
                # Trường hợp này không nên xảy ra vì đã kiểm tra quyền ở trên
                return Response({"detail": "Only doctors and admins can create diagnoses."}, status=status.HTTP_403_FORBIDDEN)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DiagnosisDetailAPIView(APIView):
    """
    API endpoint để xem, cập nhật và xóa chẩn đoán.
    """
    permission_classes = [CanViewMedicalRecords]
    authentication_classes = [CustomJWTAuthentication]

    def get_object(self, pk):
        """
        Lấy đối tượng chẩn đoán dựa trên primary key.
        """
        try:
            diagnosis = Diagnosis.objects.get(pk=pk)

            # Kiểm tra quyền truy cập
            user_role = self.request.auth.get('role', None) if self.request.auth else None
            user_id = self.request.user.id

            if user_role in ['DOCTOR', 'ADMIN', 'NURSE']:
                return diagnosis
            elif user_role == 'PATIENT' and diagnosis.medical_record.patient_id == user_id:
                return diagnosis
            else:
                return None
        except Diagnosis.DoesNotExist:
            return None

    def get(self, request, pk):
        """
        Lấy thông tin chi tiết của chẩn đoán.
        """
        diagnosis = self.get_object(pk)
        if diagnosis is None:
            return Response({"detail": "Diagnosis not found or you do not have permission to view it."}, status=status.HTTP_404_NOT_FOUND)

        # Lấy thông tin bác sĩ từ User Service
        doctor_info = UserService.get_user_info(diagnosis.doctor_id)

        # Thêm thông tin bác sĩ vào response
        serializer = DiagnosisSerializer(diagnosis)
        data = serializer.data
        if doctor_info:
            data['doctor'] = {
                'id': doctor_info.get('id'),
                'name': f"{doctor_info.get('first_name', '')} {doctor_info.get('last_name', '')}",
                'specialization': doctor_info.get('doctor_profile', {}).get('specialization', '')
            }

        return Response(data)

    def put(self, request, pk):
        """
        Cập nhật chẩn đoán.
        """
        diagnosis = self.get_object(pk)
        if diagnosis is None:
            return Response({"detail": "Diagnosis not found or you do not have permission to update it."}, status=status.HTTP_404_NOT_FOUND)

        # Chỉ bác sĩ và quản trị viên mới có thể cập nhật chẩn đoán
        user_role = request.auth.get('role', None) if request.auth else None
        if user_role not in ['DOCTOR', 'ADMIN']:
            return Response({"detail": "You do not have permission to update diagnoses."}, status=status.HTTP_403_FORBIDDEN)

        serializer = DiagnosisSerializer(diagnosis, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Xóa chẩn đoán.
        """
        diagnosis = self.get_object(pk)
        if diagnosis is None:
            return Response({"detail": "Diagnosis not found or you do not have permission to delete it."}, status=status.HTTP_404_NOT_FOUND)

        # Chỉ bác sĩ và quản trị viên mới có thể xóa chẩn đoán
        user_role = request.auth.get('role', None) if request.auth else None
        if user_role not in ['DOCTOR', 'ADMIN']:
            return Response({"detail": "You do not have permission to delete diagnoses."}, status=status.HTTP_403_FORBIDDEN)

        diagnosis.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# API cho Treatment
class TreatmentListCreateAPIView(APIView):
    """
    API endpoint để lấy danh sách và tạo mới điều trị.
    """
    permission_classes = [CanViewMedicalRecords]
    authentication_classes = [CustomJWTAuthentication]
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        """
        Lấy danh sách điều trị.
        """
        # Lấy thông tin từ JWT token
        user_role = request.auth.get('role', None) if request.auth else None
        user_id = request.user.id

        # Khởi tạo queryset
        queryset = Treatment.objects.all()

        # Nếu là bệnh nhân, chỉ trả về điều trị trong hồ sơ của chính họ
        if user_role == 'PATIENT':
            queryset = queryset.filter(diagnosis__medical_record__patient_id=user_id)

        # Lọc theo diagnosis_id nếu được cung cấp
        diagnosis_id = request.query_params.get('diagnosis_id', None)
        if diagnosis_id is not None:
            queryset = queryset.filter(diagnosis_id=diagnosis_id)

        # Tìm kiếm
        search = request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(
                Q(treatment_type__icontains=search) |
                Q(treatment_description__icontains=search)
            )

        # Sắp xếp
        ordering = request.query_params.get('ordering', '-start_date')
        if ordering:
            queryset = queryset.order_by(ordering)

        # Phân trang
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = TreatmentSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = TreatmentSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Tạo mới điều trị.
        """
        serializer = TreatmentSerializer(data=request.data)
        if serializer.is_valid():
            # Lấy thông tin người dùng
            user_role = request.auth.get('role', None) if request.auth else None
            user_id = request.user.id

            # Chỉ bác sĩ và quản trị viên mới có thể tạo điều trị
            if user_role not in ['DOCTOR', 'ADMIN']:
                return Response({"detail": "You do not have permission to create treatments."}, status=status.HTTP_403_FORBIDDEN)

            # Kiểm tra quyền truy cập vào chẩn đoán
            diagnosis_id = request.data.get('diagnosis')
            try:
                diagnosis = Diagnosis.objects.get(pk=diagnosis_id)
                if user_role == 'PATIENT' and diagnosis.medical_record.patient_id != user_id:
                    return Response({"detail": "You do not have permission to add treatments to this diagnosis."}, status=status.HTTP_403_FORBIDDEN)
            except Diagnosis.DoesNotExist:
                return Response({"detail": "Diagnosis not found."}, status=status.HTTP_404_NOT_FOUND)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TreatmentDetailAPIView(APIView):
    """
    API endpoint để xem, cập nhật và xóa điều trị.
    """
    permission_classes = [CanViewMedicalRecords]
    authentication_classes = [CustomJWTAuthentication]

    def get_object(self, pk):
        """
        Lấy đối tượng điều trị dựa trên primary key.
        """
        try:
            treatment = Treatment.objects.get(pk=pk)

            # Kiểm tra quyền truy cập
            user_role = self.request.auth.get('role', None) if self.request.auth else None
            user_id = self.request.user.id

            if user_role in ['DOCTOR', 'ADMIN', 'NURSE']:
                return treatment
            elif user_role == 'PATIENT' and treatment.diagnosis.medical_record.patient_id == user_id:
                return treatment
            else:
                return None
        except Treatment.DoesNotExist:
            return None

    def get(self, request, pk):
        """
        Lấy thông tin chi tiết của điều trị.
        """
        treatment = self.get_object(pk)
        if treatment is None:
            return Response({"detail": "Treatment not found or you do not have permission to view it."}, status=status.HTTP_404_NOT_FOUND)

        serializer = TreatmentSerializer(treatment)
        return Response(serializer.data)

    def put(self, request, pk):
        """
        Cập nhật điều trị.
        """
        treatment = self.get_object(pk)
        if treatment is None:
            return Response({"detail": "Treatment not found or you do not have permission to update it."}, status=status.HTTP_404_NOT_FOUND)

        # Chỉ bác sĩ và quản trị viên mới có thể cập nhật điều trị
        user_role = request.auth.get('role', None) if request.auth else None
        if user_role not in ['DOCTOR', 'ADMIN']:
            return Response({"detail": "You do not have permission to update treatments."}, status=status.HTTP_403_FORBIDDEN)

        serializer = TreatmentSerializer(treatment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Xóa điều trị.
        """
        treatment = self.get_object(pk)
        if treatment is None:
            return Response({"detail": "Treatment not found or you do not have permission to delete it."}, status=status.HTTP_404_NOT_FOUND)

        # Chỉ bác sĩ và quản trị viên mới có thể xóa điều trị
        user_role = request.auth.get('role', None) if request.auth else None
        if user_role not in ['DOCTOR', 'ADMIN']:
            return Response({"detail": "You do not have permission to delete treatments."}, status=status.HTTP_403_FORBIDDEN)

        treatment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# API cho Allergy
class AllergyListCreateAPIView(APIView):
    """
    API endpoint để lấy danh sách và tạo mới dị ứng.
    """
    permission_classes = [CanViewMedicalRecords]
    authentication_classes = [CustomJWTAuthentication]
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        """
        Lấy danh sách dị ứng.
        """
        # Lấy thông tin từ JWT token
        user_role = request.auth.get('role', None) if request.auth else None
        user_id = request.user.id

        # Khởi tạo queryset
        queryset = Allergy.objects.all()

        # Nếu là bệnh nhân, chỉ trả về dị ứng trong hồ sơ của chính họ
        if user_role == 'PATIENT':
            queryset = queryset.filter(medical_record__patient_id=user_id)

        # Lọc theo medical_record_id nếu được cung cấp
        medical_record_id = request.query_params.get('medical_record_id', None)
        if medical_record_id is not None:
            queryset = queryset.filter(medical_record_id=medical_record_id)

        # Tìm kiếm
        search = request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(
                Q(allergy_type__icontains=search) |
                Q(allergy_name__icontains=search)
            )

        # Sắp xếp
        ordering = request.query_params.get('ordering', '-created_at')
        if ordering:
            queryset = queryset.order_by(ordering)

        # Phân trang
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = AllergySerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = AllergySerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Tạo mới dị ứng.
        """
        serializer = AllergySerializer(data=request.data)
        if serializer.is_valid():
            # Lấy thông tin người dùng
            user_role = request.auth.get('role', None) if request.auth else None
            user_id = request.user.id

            # Chỉ bác sĩ và quản trị viên mới có thể tạo dị ứng
            if user_role not in ['DOCTOR', 'ADMIN']:
                return Response({"detail": "You do not have permission to create allergies."}, status=status.HTTP_403_FORBIDDEN)

            # Kiểm tra quyền truy cập vào hồ sơ y tế
            medical_record_id = request.data.get('medical_record')
            try:
                medical_record = MedicalRecord.objects.get(pk=medical_record_id)
                if user_role == 'PATIENT' and medical_record.patient_id != user_id:
                    return Response({"detail": "You do not have permission to add allergies to this medical record."}, status=status.HTTP_403_FORBIDDEN)
            except MedicalRecord.DoesNotExist:
                return Response({"detail": "Medical record not found."}, status=status.HTTP_404_NOT_FOUND)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AllergyDetailAPIView(APIView):
    """
    API endpoint để xem, cập nhật và xóa dị ứng.
    """
    permission_classes = [CanViewMedicalRecords]
    authentication_classes = [CustomJWTAuthentication]

    def get_object(self, pk):
        """
        Lấy đối tượng dị ứng dựa trên primary key.
        """
        try:
            allergy = Allergy.objects.get(pk=pk)

            # Kiểm tra quyền truy cập
            user_role = self.request.auth.get('role', None) if self.request.auth else None
            user_id = self.request.user.id

            if user_role in ['DOCTOR', 'ADMIN', 'NURSE']:
                return allergy
            elif user_role == 'PATIENT' and allergy.medical_record.patient_id == user_id:
                return allergy
            else:
                return None
        except Allergy.DoesNotExist:
            return None

    def get(self, request, pk):
        """
        Lấy thông tin chi tiết của dị ứng.
        """
        allergy = self.get_object(pk)
        if allergy is None:
            return Response({"detail": "Allergy not found or you do not have permission to view it."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AllergySerializer(allergy)
        return Response(serializer.data)

    def put(self, request, pk):
        """
        Cập nhật dị ứng.
        """
        allergy = self.get_object(pk)
        if allergy is None:
            return Response({"detail": "Allergy not found or you do not have permission to update it."}, status=status.HTTP_404_NOT_FOUND)

        # Chỉ bác sĩ và quản trị viên mới có thể cập nhật dị ứng
        user_role = request.auth.get('role', None) if request.auth else None
        if user_role not in ['DOCTOR', 'ADMIN']:
            return Response({"detail": "You do not have permission to update allergies."}, status=status.HTTP_403_FORBIDDEN)

        serializer = AllergySerializer(allergy, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Xóa dị ứng.
        """
        allergy = self.get_object(pk)
        if allergy is None:
            return Response({"detail": "Allergy not found or you do not have permission to delete it."}, status=status.HTTP_404_NOT_FOUND)

        # Chỉ bác sĩ và quản trị viên mới có thể xóa dị ứng
        user_role = request.auth.get('role', None) if request.auth else None
        if user_role not in ['DOCTOR', 'ADMIN']:
            return Response({"detail": "You do not have permission to delete allergies."}, status=status.HTTP_403_FORBIDDEN)

        allergy.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# API cho Immunization
class ImmunizationListCreateAPIView(APIView):
    """
    API endpoint để lấy danh sách và tạo mới tiêm chủng.
    """
    permission_classes = [CanViewMedicalRecords]
    authentication_classes = [CustomJWTAuthentication]
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        """
        Lấy danh sách tiêm chủng.
        """
        # Lấy thông tin từ JWT token
        user_role = request.auth.get('role', None) if request.auth else None
        user_id = request.user.id

        # Khởi tạo queryset
        queryset = Immunization.objects.all()

        # Nếu là bệnh nhân, chỉ trả về tiêm chủng trong hồ sơ của chính họ
        if user_role == 'PATIENT':
            queryset = queryset.filter(medical_record__patient_id=user_id)

        # Lọc theo medical_record_id nếu được cung cấp
        medical_record_id = request.query_params.get('medical_record_id', None)
        if medical_record_id is not None:
            queryset = queryset.filter(medical_record_id=medical_record_id)

        # Tìm kiếm
        search = request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(vaccine_name__icontains=search)

        # Sắp xếp
        ordering = request.query_params.get('ordering', '-administration_date')
        if ordering:
            queryset = queryset.order_by(ordering)

        # Phân trang
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = ImmunizationSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ImmunizationSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Tạo mới tiêm chủng.
        """
        serializer = ImmunizationSerializer(data=request.data)
        if serializer.is_valid():
            # Lấy thông tin người dùng
            user_role = request.auth.get('role', None) if request.auth else None
            user_id = request.user.id

            # Chỉ bác sĩ, y tá và quản trị viên mới có thể tạo tiêm chủng
            if user_role not in ['DOCTOR', 'NURSE', 'ADMIN']:
                return Response({"detail": "You do not have permission to create immunizations."}, status=status.HTTP_403_FORBIDDEN)

            # Kiểm tra quyền truy cập vào hồ sơ y tế
            medical_record_id = request.data.get('medical_record')
            try:
                medical_record = MedicalRecord.objects.get(pk=medical_record_id)
                if user_role == 'PATIENT' and medical_record.patient_id != user_id:
                    return Response({"detail": "You do not have permission to add immunizations to this medical record."}, status=status.HTTP_403_FORBIDDEN)
            except MedicalRecord.DoesNotExist:
                return Response({"detail": "Medical record not found."}, status=status.HTTP_404_NOT_FOUND)

            # Lưu thông tin người thực hiện tiêm chủng
            serializer.save(administered_by=user_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ImmunizationDetailAPIView(APIView):
    """
    API endpoint để xem, cập nhật và xóa tiêm chủng.
    """
    permission_classes = [CanViewMedicalRecords]
    authentication_classes = [CustomJWTAuthentication]

    def get_object(self, pk):
        """
        Lấy đối tượng tiêm chủng dựa trên primary key.
        """
        try:
            immunization = Immunization.objects.get(pk=pk)

            # Kiểm tra quyền truy cập
            user_role = self.request.auth.get('role', None) if self.request.auth else None
            user_id = self.request.user.id

            if user_role in ['DOCTOR', 'ADMIN', 'NURSE']:
                return immunization
            elif user_role == 'PATIENT' and immunization.medical_record.patient_id == user_id:
                return immunization
            else:
                return None
        except Immunization.DoesNotExist:
            return None

    def get(self, request, pk):
        """
        Lấy thông tin chi tiết của tiêm chủng.
        """
        immunization = self.get_object(pk)
        if immunization is None:
            return Response({"detail": "Immunization not found or you do not have permission to view it."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ImmunizationSerializer(immunization)
        return Response(serializer.data)

    def put(self, request, pk):
        """
        Cập nhật tiêm chủng.
        """
        immunization = self.get_object(pk)
        if immunization is None:
            return Response({"detail": "Immunization not found or you do not have permission to update it."}, status=status.HTTP_404_NOT_FOUND)

        # Chỉ bác sĩ, y tá và quản trị viên mới có thể cập nhật tiêm chủng
        user_role = request.auth.get('role', None) if request.auth else None
        if user_role not in ['DOCTOR', 'NURSE', 'ADMIN']:
            return Response({"detail": "You do not have permission to update immunizations."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ImmunizationSerializer(immunization, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Xóa tiêm chủng.
        """
        immunization = self.get_object(pk)
        if immunization is None:
            return Response({"detail": "Immunization not found or you do not have permission to delete it."}, status=status.HTTP_404_NOT_FOUND)

        # Chỉ bác sĩ và quản trị viên mới có thể xóa tiêm chủng
        user_role = request.auth.get('role', None) if request.auth else None
        if user_role not in ['DOCTOR', 'ADMIN']:
            return Response({"detail": "You do not have permission to delete immunizations."}, status=status.HTTP_403_FORBIDDEN)

        immunization.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# API cho Medical History
class MedicalHistoryListCreateAPIView(APIView):
    """
    API endpoint để lấy danh sách và tạo mới lịch sử bệnh án.
    """
    permission_classes = [CanViewMedicalRecords]
    authentication_classes = [CustomJWTAuthentication]
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        """
        Lấy danh sách lịch sử bệnh án.
        """
        # Lấy thông tin từ JWT token
        user_role = request.auth.get('role', None) if request.auth else None
        user_id = request.user.id

        # Khởi tạo queryset
        queryset = MedicalHistory.objects.all()

        # Nếu là bệnh nhân, chỉ trả về lịch sử bệnh án trong hồ sơ của chính họ
        if user_role == 'PATIENT':
            queryset = queryset.filter(medical_record__patient_id=user_id)

        # Lọc theo medical_record_id nếu được cung cấp
        medical_record_id = request.query_params.get('medical_record_id', None)
        if medical_record_id is not None:
            queryset = queryset.filter(medical_record_id=medical_record_id)

        # Tìm kiếm
        search = request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(condition_name__icontains=search)

        # Sắp xếp
        ordering = request.query_params.get('ordering', '-diagnosis_date')
        if ordering:
            queryset = queryset.order_by(ordering)

        # Phân trang
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = MedicalHistorySerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = MedicalHistorySerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Tạo mới lịch sử bệnh án.
        """
        serializer = MedicalHistorySerializer(data=request.data)
        if serializer.is_valid():
            # Lấy thông tin người dùng
            user_role = request.auth.get('role', None) if request.auth else None
            user_id = request.user.id

            # Chỉ bác sĩ và quản trị viên mới có thể tạo lịch sử bệnh án
            if user_role not in ['DOCTOR', 'ADMIN']:
                return Response({"detail": "You do not have permission to create medical histories."}, status=status.HTTP_403_FORBIDDEN)

            # Kiểm tra quyền truy cập vào hồ sơ y tế
            medical_record_id = request.data.get('medical_record')
            try:
                medical_record = MedicalRecord.objects.get(pk=medical_record_id)
                if user_role == 'PATIENT' and medical_record.patient_id != user_id:
                    return Response({"detail": "You do not have permission to add medical histories to this medical record."}, status=status.HTTP_403_FORBIDDEN)
            except MedicalRecord.DoesNotExist:
                return Response({"detail": "Medical record not found."}, status=status.HTTP_404_NOT_FOUND)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MedicalHistoryDetailAPIView(APIView):
    """
    API endpoint để xem, cập nhật và xóa lịch sử bệnh án.
    """
    permission_classes = [CanViewMedicalRecords]
    authentication_classes = [CustomJWTAuthentication]

    def get_object(self, pk):
        """
        Lấy đối tượng lịch sử bệnh án dựa trên primary key.
        """
        try:
            medical_history = MedicalHistory.objects.get(pk=pk)

            # Kiểm tra quyền truy cập
            user_role = self.request.auth.get('role', None) if self.request.auth else None
            user_id = self.request.user.id

            if user_role in ['DOCTOR', 'ADMIN', 'NURSE']:
                return medical_history
            elif user_role == 'PATIENT' and medical_history.medical_record.patient_id == user_id:
                return medical_history
            else:
                return None
        except MedicalHistory.DoesNotExist:
            return None

    def get(self, request, pk):
        """
        Lấy thông tin chi tiết của lịch sử bệnh án.
        """
        medical_history = self.get_object(pk)
        if medical_history is None:
            return Response({"detail": "Medical history not found or you do not have permission to view it."}, status=status.HTTP_404_NOT_FOUND)

        serializer = MedicalHistorySerializer(medical_history)
        return Response(serializer.data)

    def put(self, request, pk):
        """
        Cập nhật lịch sử bệnh án.
        """
        medical_history = self.get_object(pk)
        if medical_history is None:
            return Response({"detail": "Medical history not found or you do not have permission to update it."}, status=status.HTTP_404_NOT_FOUND)

        # Chỉ bác sĩ và quản trị viên mới có thể cập nhật lịch sử bệnh án
        user_role = request.auth.get('role', None) if request.auth else None
        if user_role not in ['DOCTOR', 'ADMIN']:
            return Response({"detail": "You do not have permission to update medical histories."}, status=status.HTTP_403_FORBIDDEN)

        serializer = MedicalHistorySerializer(medical_history, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Xóa lịch sử bệnh án.
        """
        medical_history = self.get_object(pk)
        if medical_history is None:
            return Response({"detail": "Medical history not found or you do not have permission to delete it."}, status=status.HTTP_404_NOT_FOUND)

        # Chỉ bác sĩ và quản trị viên mới có thể xóa lịch sử bệnh án
        user_role = request.auth.get('role', None) if request.auth else None
        if user_role not in ['DOCTOR', 'ADMIN']:
            return Response({"detail": "You do not have permission to delete medical histories."}, status=status.HTTP_403_FORBIDDEN)

        medical_history.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# API cho Medication
class MedicationListCreateAPIView(APIView):
    """
    API endpoint để lấy danh sách và tạo mới thuốc.
    """
    permission_classes = [CanViewMedicalRecords]
    authentication_classes = [CustomJWTAuthentication]
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        """
        Lấy danh sách thuốc.
        """
        # Lấy thông tin từ JWT token
        user_role = request.auth.get('role', None) if request.auth else None
        user_id = request.user.id

        # Khởi tạo queryset
        queryset = Medication.objects.all()

        # Nếu là bệnh nhân, chỉ trả về thuốc trong hồ sơ của chính họ
        if user_role == 'PATIENT':
            queryset = queryset.filter(medical_record__patient_id=user_id)

        # Lọc theo medical_record_id nếu được cung cấp
        medical_record_id = request.query_params.get('medical_record_id', None)
        if medical_record_id is not None:
            queryset = queryset.filter(medical_record_id=medical_record_id)

        # Tìm kiếm
        search = request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(
                Q(medication_name__icontains=search) |
                Q(dosage__icontains=search)
            )

        # Sắp xếp
        ordering = request.query_params.get('ordering', '-start_date')
        if ordering:
            queryset = queryset.order_by(ordering)

        # Phân trang
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = MedicationSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = MedicationSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Tạo mới thuốc.
        """
        serializer = MedicationSerializer(data=request.data)
        if serializer.is_valid():
            # Lấy thông tin người dùng
            user_role = request.auth.get('role', None) if request.auth else None
            user_id = request.user.id

            # Chỉ bác sĩ và quản trị viên mới có thể tạo thuốc
            if user_role not in ['DOCTOR', 'ADMIN']:
                return Response({"detail": "You do not have permission to create medications."}, status=status.HTTP_403_FORBIDDEN)

            # Kiểm tra quyền truy cập vào hồ sơ y tế
            medical_record_id = request.data.get('medical_record')
            try:
                medical_record = MedicalRecord.objects.get(pk=medical_record_id)
                if user_role == 'PATIENT' and medical_record.patient_id != user_id:
                    return Response({"detail": "You do not have permission to add medications to this medical record."}, status=status.HTTP_403_FORBIDDEN)
            except MedicalRecord.DoesNotExist:
                return Response({"detail": "Medical record not found."}, status=status.HTTP_404_NOT_FOUND)

            # Lưu thông tin bác sĩ kê đơn
            serializer.save(prescribed_by=user_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MedicationDetailAPIView(APIView):
    """
    API endpoint để xem, cập nhật và xóa thuốc.
    """
    permission_classes = [CanViewMedicalRecords]
    authentication_classes = [CustomJWTAuthentication]

    def get_object(self, pk):
        """
        Lấy đối tượng thuốc dựa trên primary key.
        """
        try:
            medication = Medication.objects.get(pk=pk)

            # Kiểm tra quyền truy cập
            user_role = self.request.auth.get('role', None) if self.request.auth else None
            user_id = self.request.user.id

            if user_role in ['DOCTOR', 'ADMIN', 'NURSE']:
                return medication
            elif user_role == 'PATIENT' and medication.medical_record.patient_id == user_id:
                return medication
            else:
                return None
        except Medication.DoesNotExist:
            return None

    def get(self, request, pk):
        """
        Lấy thông tin chi tiết của thuốc.
        """
        medication = self.get_object(pk)
        if medication is None:
            return Response({"detail": "Medication not found or you do not have permission to view it."}, status=status.HTTP_404_NOT_FOUND)

        serializer = MedicationSerializer(medication)
        return Response(serializer.data)

    def put(self, request, pk):
        """
        Cập nhật thuốc.
        """
        medication = self.get_object(pk)
        if medication is None:
            return Response({"detail": "Medication not found or you do not have permission to update it."}, status=status.HTTP_404_NOT_FOUND)

        # Chỉ bác sĩ và quản trị viên mới có thể cập nhật thuốc
        user_role = request.auth.get('role', None) if request.auth else None
        if user_role not in ['DOCTOR', 'ADMIN']:
            return Response({"detail": "You do not have permission to update medications."}, status=status.HTTP_403_FORBIDDEN)

        serializer = MedicationSerializer(medication, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Xóa thuốc.
        """
        medication = self.get_object(pk)
        if medication is None:
            return Response({"detail": "Medication not found or you do not have permission to delete it."}, status=status.HTTP_404_NOT_FOUND)

        # Chỉ bác sĩ và quản trị viên mới có thể xóa thuốc
        user_role = request.auth.get('role', None) if request.auth else None
        if user_role not in ['DOCTOR', 'ADMIN']:
            return Response({"detail": "You do not have permission to delete medications."}, status=status.HTTP_403_FORBIDDEN)

        medication.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# API cho Vital Sign
class VitalSignListCreateAPIView(APIView):
    """
    API endpoint để lấy danh sách và tạo mới dấu hiệu sinh tồn.
    """
    permission_classes = [CanViewMedicalRecords]
    authentication_classes = [CustomJWTAuthentication]
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        """
        Lấy danh sách dấu hiệu sinh tồn.
        """
        # Lấy thông tin từ JWT token
        user_role = request.auth.get('role', None) if request.auth else None
        user_id = request.user.id

        # Khởi tạo queryset
        queryset = VitalSign.objects.all()

        # Nếu là bệnh nhân, chỉ trả về dấu hiệu sinh tồn trong hồ sơ của chính họ
        if user_role == 'PATIENT':
            queryset = queryset.filter(medical_record__patient_id=user_id)

        # Lọc theo medical_record_id nếu được cung cấp
        medical_record_id = request.query_params.get('medical_record_id', None)
        if medical_record_id is not None:
            queryset = queryset.filter(medical_record_id=medical_record_id)

        # Tìm kiếm
        search = request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(vital_type__icontains=search)

        # Sắp xếp
        ordering = request.query_params.get('ordering', '-recorded_at')
        if ordering:
            queryset = queryset.order_by(ordering)

        # Phân trang
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = VitalSignSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = VitalSignSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Tạo mới dấu hiệu sinh tồn.
        """
        serializer = VitalSignSerializer(data=request.data)
        if serializer.is_valid():
            # Lấy thông tin người dùng
            user_role = request.auth.get('role', None) if request.auth else None
            user_id = request.user.id

            # Chỉ bác sĩ, y tá và quản trị viên mới có thể tạo dấu hiệu sinh tồn
            if user_role not in ['DOCTOR', 'NURSE', 'ADMIN']:
                return Response({"detail": "You do not have permission to create vital signs."}, status=status.HTTP_403_FORBIDDEN)

            # Kiểm tra quyền truy cập vào hồ sơ y tế
            medical_record_id = request.data.get('medical_record')
            try:
                medical_record = MedicalRecord.objects.get(pk=medical_record_id)
                if user_role == 'PATIENT' and medical_record.patient_id != user_id:
                    return Response({"detail": "You do not have permission to add vital signs to this medical record."}, status=status.HTTP_403_FORBIDDEN)
            except MedicalRecord.DoesNotExist:
                return Response({"detail": "Medical record not found."}, status=status.HTTP_404_NOT_FOUND)

            # Lưu thông tin người ghi nhận
            serializer.save(recorded_by=user_id, recorded_at=timezone.now())
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VitalSignDetailAPIView(APIView):
    """
    API endpoint để xem, cập nhật và xóa dấu hiệu sinh tồn.
    """
    permission_classes = [CanViewMedicalRecords]
    authentication_classes = [CustomJWTAuthentication]

    def get_object(self, pk):
        """
        Lấy đối tượng dấu hiệu sinh tồn dựa trên primary key.
        """
        try:
            vital_sign = VitalSign.objects.get(pk=pk)

            # Kiểm tra quyền truy cập
            user_role = self.request.auth.get('role', None) if self.request.auth else None
            user_id = self.request.user.id

            if user_role in ['DOCTOR', 'ADMIN', 'NURSE']:
                return vital_sign
            elif user_role == 'PATIENT' and vital_sign.medical_record.patient_id == user_id:
                return vital_sign
            else:
                return None
        except VitalSign.DoesNotExist:
            return None

    def get(self, request, pk):
        """
        Lấy thông tin chi tiết của dấu hiệu sinh tồn.
        """
        vital_sign = self.get_object(pk)
        if vital_sign is None:
            return Response({"detail": "Vital sign not found or you do not have permission to view it."}, status=status.HTTP_404_NOT_FOUND)

        serializer = VitalSignSerializer(vital_sign)
        return Response(serializer.data)

    def put(self, request, pk):
        """
        Cập nhật dấu hiệu sinh tồn.
        """
        vital_sign = self.get_object(pk)
        if vital_sign is None:
            return Response({"detail": "Vital sign not found or you do not have permission to update it."}, status=status.HTTP_404_NOT_FOUND)

        # Chỉ bác sĩ, y tá và quản trị viên mới có thể cập nhật dấu hiệu sinh tồn
        user_role = request.auth.get('role', None) if request.auth else None
        if user_role not in ['DOCTOR', 'NURSE', 'ADMIN']:
            return Response({"detail": "You do not have permission to update vital signs."}, status=status.HTTP_403_FORBIDDEN)

        serializer = VitalSignSerializer(vital_sign, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Xóa dấu hiệu sinh tồn.
        """
        vital_sign = self.get_object(pk)
        if vital_sign is None:
            return Response({"detail": "Vital sign not found or you do not have permission to delete it."}, status=status.HTTP_404_NOT_FOUND)

        # Chỉ bác sĩ và quản trị viên mới có thể xóa dấu hiệu sinh tồn
        user_role = request.auth.get('role', None) if request.auth else None
        if user_role not in ['DOCTOR', 'ADMIN']:
            return Response({"detail": "You do not have permission to delete vital signs."}, status=status.HTTP_403_FORBIDDEN)

        vital_sign.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# API cho Lab Test
class LabTestListCreateAPIView(APIView):
    """
    API endpoint để lấy danh sách và tạo mới xét nghiệm.
    """
    permission_classes = [CanViewMedicalRecords]
    authentication_classes = [CustomJWTAuthentication]
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        """
        Lấy danh sách xét nghiệm.
        """
        # Lấy thông tin từ JWT token
        user_role = request.auth.get('role', None) if request.auth else None
        user_id = request.user.id

        # Khởi tạo queryset
        queryset = LabTest.objects.all()

        # Nếu là bệnh nhân, chỉ trả về xét nghiệm trong hồ sơ của chính họ
        if user_role == 'PATIENT':
            queryset = queryset.filter(medical_record__patient_id=user_id)

        # Lọc theo medical_record_id nếu được cung cấp
        medical_record_id = request.query_params.get('medical_record_id', None)
        if medical_record_id is not None:
            queryset = queryset.filter(medical_record_id=medical_record_id)

        # Tìm kiếm
        search = request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(
                Q(test_name__icontains=search) |
                Q(test_code__icontains=search)
            )

        # Sắp xếp
        ordering = request.query_params.get('ordering', '-ordered_at')
        if ordering:
            queryset = queryset.order_by(ordering)

        # Phân trang
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = LabTestSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = LabTestSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Tạo mới xét nghiệm.
        """
        serializer = LabTestSerializer(data=request.data)
        if serializer.is_valid():
            # Lấy thông tin người dùng
            user_role = request.auth.get('role', None) if request.auth else None
            user_id = request.user.id

            # Chỉ bác sĩ và quản trị viên mới có thể tạo xét nghiệm
            if user_role not in ['DOCTOR', 'ADMIN']:
                return Response({"detail": "You do not have permission to create lab tests."}, status=status.HTTP_403_FORBIDDEN)

            # Kiểm tra quyền truy cập vào hồ sơ y tế
            medical_record_id = request.data.get('medical_record')
            try:
                medical_record = MedicalRecord.objects.get(pk=medical_record_id)
                if user_role == 'PATIENT' and medical_record.patient_id != user_id:
                    return Response({"detail": "You do not have permission to add lab tests to this medical record."}, status=status.HTTP_403_FORBIDDEN)
            except MedicalRecord.DoesNotExist:
                return Response({"detail": "Medical record not found."}, status=status.HTTP_404_NOT_FOUND)

            # Lưu thông tin bác sĩ yêu cầu xét nghiệm
            serializer.save(ordered_by=user_id, ordered_at=timezone.now())
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LabTestDetailAPIView(APIView):
    """
    API endpoint để xem, cập nhật và xóa xét nghiệm.
    """
    permission_classes = [CanViewMedicalRecords]
    authentication_classes = [CustomJWTAuthentication]

    def get_object(self, pk):
        """
        Lấy đối tượng xét nghiệm dựa trên primary key.
        """
        try:
            lab_test = LabTest.objects.get(pk=pk)

            # Kiểm tra quyền truy cập
            user_role = self.request.auth.get('role', None) if self.request.auth else None
            user_id = self.request.user.id

            if user_role in ['DOCTOR', 'ADMIN', 'NURSE']:
                return lab_test
            elif user_role == 'PATIENT' and lab_test.medical_record.patient_id == user_id:
                return lab_test
            else:
                return None
        except LabTest.DoesNotExist:
            return None

    def get(self, request, pk):
        """
        Lấy thông tin chi tiết của xét nghiệm.
        """
        lab_test = self.get_object(pk)
        if lab_test is None:
            return Response({"detail": "Lab test not found or you do not have permission to view it."}, status=status.HTTP_404_NOT_FOUND)

        serializer = LabTestSerializer(lab_test)
        return Response(serializer.data)

    def put(self, request, pk):
        """
        Cập nhật xét nghiệm.
        """
        lab_test = self.get_object(pk)
        if lab_test is None:
            return Response({"detail": "Lab test not found or you do not have permission to update it."}, status=status.HTTP_404_NOT_FOUND)

        # Chỉ bác sĩ, kỹ thuật viên và quản trị viên mới có thể cập nhật xét nghiệm
        user_role = request.auth.get('role', None) if request.auth else None
        if user_role not in ['DOCTOR', 'LAB_TECHNICIAN', 'ADMIN']:
            return Response({"detail": "You do not have permission to update lab tests."}, status=status.HTTP_403_FORBIDDEN)

        serializer = LabTestSerializer(lab_test, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Xóa xét nghiệm.
        """
        lab_test = self.get_object(pk)
        if lab_test is None:
            return Response({"detail": "Lab test not found or you do not have permission to delete it."}, status=status.HTTP_404_NOT_FOUND)

        # Chỉ bác sĩ và quản trị viên mới có thể xóa xét nghiệm
        user_role = request.auth.get('role', None) if request.auth else None
        if user_role not in ['DOCTOR', 'ADMIN']:
            return Response({"detail": "You do not have permission to delete lab tests."}, status=status.HTTP_403_FORBIDDEN)

        lab_test.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# API cho Lab Result
class LabResultListCreateAPIView(APIView):
    """
    API endpoint để lấy danh sách và tạo mới kết quả xét nghiệm.
    """
    permission_classes = [CanViewMedicalRecords]
    authentication_classes = [CustomJWTAuthentication]
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        """
        Lấy danh sách kết quả xét nghiệm.
        """
        # Lấy thông tin từ JWT token
        user_role = request.auth.get('role', None) if request.auth else None
        user_id = request.user.id

        # Khởi tạo queryset
        queryset = LabResult.objects.all()

        # Nếu là bệnh nhân, chỉ trả về kết quả xét nghiệm trong hồ sơ của chính họ
        if user_role == 'PATIENT':
            queryset = queryset.filter(lab_test__medical_record__patient_id=user_id)

        # Lọc theo lab_test_id nếu được cung cấp
        lab_test_id = request.query_params.get('lab_test_id', None)
        if lab_test_id is not None:
            queryset = queryset.filter(lab_test_id=lab_test_id)

        # Tìm kiếm
        search = request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(result_value__icontains=search)

        # Sắp xếp
        ordering = request.query_params.get('ordering', '-performed_at')
        if ordering:
            queryset = queryset.order_by(ordering)

        # Phân trang
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = LabResultSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = LabResultSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Tạo mới kết quả xét nghiệm.
        """
        serializer = LabResultSerializer(data=request.data)
        if serializer.is_valid():
            # Lấy thông tin người dùng
            user_role = request.auth.get('role', None) if request.auth else None
            user_id = request.user.id

            # Chỉ kỹ thuật viên và quản trị viên mới có thể tạo kết quả xét nghiệm
            if user_role not in ['LAB_TECHNICIAN', 'ADMIN']:
                return Response({"detail": "You do not have permission to create lab results."}, status=status.HTTP_403_FORBIDDEN)

            # Kiểm tra quyền truy cập vào xét nghiệm
            lab_test_id = request.data.get('lab_test')
            try:
                lab_test = LabTest.objects.get(pk=lab_test_id)
                if user_role == 'PATIENT' and lab_test.medical_record.patient_id != user_id:
                    return Response({"detail": "You do not have permission to add results to this lab test."}, status=status.HTTP_403_FORBIDDEN)
            except LabTest.DoesNotExist:
                return Response({"detail": "Lab test not found."}, status=status.HTTP_404_NOT_FOUND)

            # Lưu thông tin người thực hiện xét nghiệm
            serializer.save(performed_by=user_id, performed_at=timezone.now())
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LabResultDetailAPIView(APIView):
    """
    API endpoint để xem, cập nhật và xóa kết quả xét nghiệm.
    """
    permission_classes = [CanViewMedicalRecords]
    authentication_classes = [CustomJWTAuthentication]

    def get_object(self, pk):
        """
        Lấy đối tượng kết quả xét nghiệm dựa trên primary key.
        """
        try:
            lab_result = LabResult.objects.get(pk=pk)

            # Kiểm tra quyền truy cập
            user_role = self.request.auth.get('role', None) if self.request.auth else None
            user_id = self.request.user.id

            if user_role in ['DOCTOR', 'ADMIN', 'NURSE', 'LAB_TECHNICIAN']:
                return lab_result
            elif user_role == 'PATIENT' and lab_result.lab_test.medical_record.patient_id == user_id:
                return lab_result
            else:
                return None
        except LabResult.DoesNotExist:
            return None

    def get(self, request, pk):
        """
        Lấy thông tin chi tiết của kết quả xét nghiệm.
        """
        lab_result = self.get_object(pk)
        if lab_result is None:
            return Response({"detail": "Lab result not found or you do not have permission to view it."}, status=status.HTTP_404_NOT_FOUND)

        serializer = LabResultSerializer(lab_result)
        return Response(serializer.data)

    def put(self, request, pk):
        """
        Cập nhật kết quả xét nghiệm.
        """
        lab_result = self.get_object(pk)
        if lab_result is None:
            return Response({"detail": "Lab result not found or you do not have permission to update it."}, status=status.HTTP_404_NOT_FOUND)

        # Chỉ kỹ thuật viên và quản trị viên mới có thể cập nhật kết quả xét nghiệm
        user_role = request.auth.get('role', None) if request.auth else None
        if user_role not in ['LAB_TECHNICIAN', 'ADMIN']:
            return Response({"detail": "You do not have permission to update lab results."}, status=status.HTTP_403_FORBIDDEN)

        serializer = LabResultSerializer(lab_result, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Xóa kết quả xét nghiệm.
        """
        lab_result = self.get_object(pk)
        if lab_result is None:
            return Response({"detail": "Lab result not found or you do not have permission to delete it."}, status=status.HTTP_404_NOT_FOUND)

        # Chỉ kỹ thuật viên và quản trị viên mới có thể xóa kết quả xét nghiệm
        user_role = request.auth.get('role', None) if request.auth else None
        if user_role not in ['LAB_TECHNICIAN', 'ADMIN']:
            return Response({"detail": "You do not have permission to delete lab results."}, status=status.HTTP_403_FORBIDDEN)

        lab_result.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
