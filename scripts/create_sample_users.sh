#!/bin/bash

# Script để tạo các tài khoản mẫu trong hệ thống Healthcare
# Chạy script này từ thư mục gốc của dự án

# Kiểm tra xem container user-service có đang chạy không
if ! docker ps | grep -q health-care-user-service; then
    echo "Container user-service không đang chạy. Vui lòng khởi động hệ thống trước."
    exit 1
fi

# Tạo thư mục scripts trong container nếu chưa tồn tại
docker exec -it health-care-user-service-1 mkdir -p /app/scripts

# Sao chép script Python vào container
echo "Sao chép script vào container user-service..."
docker cp scripts/create_sample_users.py health-care-user-service-1:/app/scripts/

# Chạy script Python trong container
echo "Đang tạo các tài khoản mẫu..."
docker exec -it health-care-user-service-1 python /app/scripts/create_sample_users.py

# Kiểm tra kết quả
if [ $? -eq 0 ]; then
    echo "Tạo các tài khoản mẫu thành công!"
    echo "Bạn có thể đăng nhập với các tài khoản sau (mật khẩu: 123456):"
    echo "- Admin: admin@gmail.com"
    echo "- Bác sĩ: doctor@gmail.com"
    echo "- Y tá: nurse@gmail.com"
    echo "- Bệnh nhân: patient@gmail.com"
    echo "- Bệnh nhân 2: thangdz1501@gmail.com"
    echo "- Dược sĩ: pharmacist@gmail.com"
    echo "- Kỹ thuật viên xét nghiệm: labtech@gmail.com"
    echo "- Bảo hiểm: insurance@gmail.com"
else
    echo "Tạo các tài khoản mẫu thất bại. Vui lòng kiểm tra lỗi ở trên."
fi
