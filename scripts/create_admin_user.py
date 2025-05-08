#!/usr/bin/env python
"""
Script để tạo tài khoản admin trong hệ thống Healthcare.
Chạy script này từ thư mục gốc của dự án.

Sử dụng:
    docker exec -it health-care-user-service-1 python /app/scripts/create_admin_user.py \
        --email admin@gmail.com \
        --password 123456 \
        --first_name Admin \
        --last_name User

Hoặc chạy với các tham số mặc định:
    docker exec -it health-care-user-service-1 python /app/scripts/create_admin_user.py
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
from users.models import AdminProfile


def create_admin_user(email, password, first_name, last_name, admin_type='SYSTEM', 
                     position='System Administrator', employee_id='ADMIN001', 
                     access_level=5, department='IT'):
    """
    Tạo tài khoản admin và profile tương ứng.
    
    Args:
        email (str): Email của admin
        password (str): Mật khẩu của admin
        first_name (str): Tên của admin
        last_name (str): Họ của admin
        admin_type (str): Loại admin (SYSTEM, CLINIC, BILLING)
        position (str): Vị trí công việc
        employee_id (str): Mã nhân viên
        access_level (int): Cấp độ truy cập (1-5)
        department (str): Phòng ban
    
    Returns:
        tuple: (User, AdminProfile) nếu thành công, (None, None) nếu thất bại
    """
    try:
        with transaction.atomic():
            # Kiểm tra xem email đã tồn tại chưa
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                print(f"Người dùng với email {email} đã tồn tại.")
                
                # Cập nhật thông tin nếu cần
                if user.role != UserRole.ADMIN:
                    user.role = UserRole.ADMIN
                    user.is_staff = True
                    user.is_superuser = True
                    user.save()
                    print(f"Đã cập nhật vai trò của {email} thành ADMIN.")
            else:
                # Tạo tài khoản admin mới
                user = User.objects.create_superuser(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    role=UserRole.ADMIN
                )
                print(f"Đã tạo tài khoản admin mới với email {email}.")
            
            # Kiểm tra và tạo AdminProfile nếu chưa có
            try:
                admin_profile = AdminProfile.objects.get(user=user)
                print(f"Hồ sơ admin cho {email} đã tồn tại.")
            except AdminProfile.DoesNotExist:
                admin_profile = AdminProfile.objects.create(
                    user=user,
                    admin_type=admin_type,
                    position=position,
                    employee_id=employee_id,
                    access_level=access_level,
                    department=department
                )
                print(f"Đã tạo hồ sơ admin cho {email}.")
            
            return user, admin_profile
    except Exception as e:
        print(f"Lỗi khi tạo tài khoản admin: {str(e)}")
        return None, None


def main():
    parser = argparse.ArgumentParser(description='Tạo tài khoản admin cho hệ thống Healthcare')
    parser.add_argument('--email', default='admin@gmail.com', help='Email của admin')
    parser.add_argument('--password', default='123456', help='Mật khẩu của admin')
    parser.add_argument('--first_name', default='Admin', help='Tên của admin')
    parser.add_argument('--last_name', default='User', help='Họ của admin')
    parser.add_argument('--admin_type', default='SYSTEM', help='Loại admin (SYSTEM, CLINIC, BILLING)')
    parser.add_argument('--position', default='System Administrator', help='Vị trí công việc')
    parser.add_argument('--employee_id', default='ADMIN001', help='Mã nhân viên')
    parser.add_argument('--access_level', type=int, default=5, help='Cấp độ truy cập (1-5)')
    parser.add_argument('--department', default='IT', help='Phòng ban')
    
    args = parser.parse_args()
    
    print("Bắt đầu tạo tài khoản admin...")
    user, profile = create_admin_user(
        email=args.email,
        password=args.password,
        first_name=args.first_name,
        last_name=args.last_name,
        admin_type=args.admin_type,
        position=args.position,
        employee_id=args.employee_id,
        access_level=args.access_level,
        department=args.department
    )
    
    if user and profile:
        print("=== Tạo tài khoản admin thành công ===")
        print(f"Email: {user.email}")
        print(f"Họ và tên: {user.first_name} {user.last_name}")
        print(f"Vai trò: {user.role}")
        print(f"Vị trí: {profile.position}")
        print(f"Phòng ban: {profile.department}")
        print(f"Cấp độ truy cập: {profile.access_level}")
        print("=====================================")
        return 0
    else:
        print("Tạo tài khoản admin thất bại.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
