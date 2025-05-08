#!/usr/bin/env python
"""
Script để tạo các tài khoản mẫu trong hệ thống Healthcare.
Chạy script này từ thư mục gốc của dự án.

Sử dụng:
    docker exec -it health-care-user-service-1 python /app/scripts/create_sample_users.py
"""

import os
import sys
import django
import argparse
from django.db import transaction

# Thiết lập môi trường Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Import các model sau khi đã thiết lập môi trường Django
from authentication.models import User, UserRole
from users.models import (
    PatientProfile, DoctorProfile, NurseProfile, 
    PharmacistProfile, LabTechnicianProfile, 
    InsuranceProviderProfile, AdminProfile
)


def create_user(email, password, first_name, last_name, role, **profile_data):
    """
    Tạo người dùng và profile tương ứng.
    
    Args:
        email (str): Email của người dùng
        password (str): Mật khẩu của người dùng
        first_name (str): Tên của người dùng
        last_name (str): Họ của người dùng
        role (str): Vai trò của người dùng (PATIENT, DOCTOR, NURSE, ...)
        profile_data (dict): Dữ liệu cho profile tương ứng
    
    Returns:
        tuple: (User, Profile) nếu thành công, (None, None) nếu thất bại
    """
    try:
        with transaction.atomic():
            # Kiểm tra xem email đã tồn tại chưa
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                print(f"Người dùng với email {email} đã tồn tại.")
                
                # Cập nhật thông tin nếu cần
                if user.role != role:
                    user.role = role
                    user.save()
                    print(f"Đã cập nhật vai trò của {email} thành {role}.")
            else:
                # Tạo người dùng mới
                is_staff = role == UserRole.ADMIN
                is_superuser = role == UserRole.ADMIN
                
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    role=role,
                    is_staff=is_staff,
                    is_superuser=is_superuser
                )
                print(f"Đã tạo người dùng mới với email {email} và vai trò {role}.")
            
            # Tạo profile tương ứng
            profile = None
            if role == UserRole.PATIENT:
                profile, created = PatientProfile.objects.get_or_create(
                    user=user,
                    defaults=profile_data
                )
            elif role == UserRole.DOCTOR:
                profile, created = DoctorProfile.objects.get_or_create(
                    user=user,
                    defaults=profile_data
                )
            elif role == UserRole.NURSE:
                profile, created = NurseProfile.objects.get_or_create(
                    user=user,
                    defaults=profile_data
                )
            elif role == UserRole.ADMIN:
                profile, created = AdminProfile.objects.get_or_create(
                    user=user,
                    defaults=profile_data
                )
            elif role == UserRole.PHARMACIST:
                profile, created = PharmacistProfile.objects.get_or_create(
                    user=user,
                    defaults=profile_data
                )
            elif role == UserRole.LAB_TECH:
                profile, created = LabTechnicianProfile.objects.get_or_create(
                    user=user,
                    defaults=profile_data
                )
            elif role == UserRole.INSURANCE:
                profile, created = InsuranceProviderProfile.objects.get_or_create(
                    user=user,
                    defaults=profile_data
                )
            
            if created:
                print(f"Đã tạo hồ sơ {role} cho {email}.")
            else:
                print(f"Hồ sơ {role} cho {email} đã tồn tại.")
            
            return user, profile
    except Exception as e:
        print(f"Lỗi khi tạo người dùng: {str(e)}")
        return None, None


def create_sample_users():
    """Tạo các tài khoản mẫu cho hệ thống"""
    
    # Tạo tài khoản admin
    admin, _ = create_user(
        email="admin@gmail.com",
        password="123456",
        first_name="Admin",
        last_name="User",
        role=UserRole.ADMIN,
        admin_type="SYSTEM",
        position="System Administrator",
        employee_id="ADMIN001",
        access_level=5,
        department="IT"
    )
    
    # Tạo tài khoản bác sĩ
    doctor, _ = create_user(
        email="doctor@gmail.com",
        password="123456",
        first_name="Bác sĩ",
        last_name="Nguyễn",
        role=UserRole.DOCTOR,
        specialization="Tim mạch",
        license_number="BS12345",
        years_of_experience=10,
        education="Đại học Y Hà Nội",
        certifications="Chứng chỉ hành nghề bác sĩ",
        languages_spoken="Tiếng Việt, Tiếng Anh"
    )
    
    # Tạo tài khoản y tá
    nurse, _ = create_user(
        email="nurse@gmail.com",
        password="123456",
        first_name="Y tá",
        last_name="Trần",
        role=UserRole.NURSE,
        license_number="YT67890",
        department="Tim mạch",
        years_of_experience=5
    )
    
    # Tạo tài khoản bệnh nhân
    patient, _ = create_user(
        email="patient@gmail.com",
        password="123456",
        first_name="Bệnh nhân",
        last_name="Lê",
        role=UserRole.PATIENT,
        date_of_birth="1990-01-01",
        gender="M",
        blood_type="A+",
        height=170,
        weight=70,
        emergency_contact_name="Người thân",
        emergency_contact_phone="0987654321"
    )
    
    # Tạo tài khoản dược sĩ
    pharmacist, _ = create_user(
        email="pharmacist@gmail.com",
        password="123456",
        first_name="Dược sĩ",
        last_name="Phạm",
        role=UserRole.PHARMACIST,
        license_number="DS54321",
        specialization="Dược lâm sàng",
        pharmacy_name="Nhà thuốc Minh Châu"
    )
    
    # Tạo tài khoản kỹ thuật viên xét nghiệm
    lab_tech, _ = create_user(
        email="labtech@gmail.com",
        password="123456",
        first_name="Kỹ thuật viên",
        last_name="Hoàng",
        role=UserRole.LAB_TECH,
        license_number="KTV98765",
        specialization="Xét nghiệm máu",
        laboratory_name="Phòng xét nghiệm Trung tâm"
    )
    
    # Tạo tài khoản bảo hiểm
    insurance, _ = create_user(
        email="insurance@gmail.com",
        password="123456",
        first_name="Bảo hiểm",
        last_name="Vũ",
        role=UserRole.INSURANCE,
        company_name="Bảo hiểm Y tế Việt Nam",
        provider_id="BH24680",
        coverage_details="Bảo hiểm y tế toàn diện"
    )
    
    # Tạo tài khoản bệnh nhân thứ hai (thangdz1501@gmail.com)
    patient2, _ = create_user(
        email="thangdz1501@gmail.com",
        password="123456",
        first_name="Thắng",
        last_name="Nguyễn",
        role=UserRole.PATIENT,
        date_of_birth="1995-01-15",
        gender="M",
        blood_type="O+",
        height=175,
        weight=68,
        emergency_contact_name="Người thân",
        emergency_contact_phone="0912345678"
    )
    
    return {
        "admin": admin,
        "doctor": doctor,
        "nurse": nurse,
        "patient": patient,
        "patient2": patient2,
        "pharmacist": pharmacist,
        "lab_tech": lab_tech,
        "insurance": insurance
    }


def main():
    parser = argparse.ArgumentParser(description='Tạo các tài khoản mẫu cho hệ thống Healthcare')
    parser.add_argument('--force', action='store_true', help='Ghi đè các tài khoản đã tồn tại')
    
    args = parser.parse_args()
    
    print("Bắt đầu tạo các tài khoản mẫu...")
    users = create_sample_users()
    
    if all(users.values()):
        print("=== Tạo các tài khoản mẫu thành công ===")
        print("Danh sách tài khoản:")
        for role, user in users.items():
            print(f"- {role}: {user.email} (mật khẩu: 123456)")
        print("=======================================")
        return 0
    else:
        print("Tạo các tài khoản mẫu thất bại.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
