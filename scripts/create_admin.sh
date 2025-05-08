#!/bin/bash

# Script để tạo tài khoản admin trong hệ thống Healthcare
# Chạy script này từ thư mục gốc của dự án

# Kiểm tra xem container user-service có đang chạy không
if ! docker ps | grep -q health-care-user-service; then
    echo "Container user-service không đang chạy. Vui lòng khởi động hệ thống trước."
    exit 1
fi

# Sao chép script Python vào container
echo "Sao chép script vào container user-service..."
docker cp scripts/create_admin_user.py health-care-user-service-1:/app/scripts/

# Thiết lập các tham số mặc định
EMAIL=${1:-"admin@gmail.com"}
PASSWORD=${2:-"123456"}
FIRST_NAME=${3:-"Admin"}
LAST_NAME=${4:-"User"}

# Chạy script Python trong container
echo "Đang tạo tài khoản admin..."
docker exec -it health-care-user-service-1 python /app/scripts/create_admin_user.py \
    --email "$EMAIL" \
    --password "$PASSWORD" \
    --first_name "$FIRST_NAME" \
    --last_name "$LAST_NAME"

# Kiểm tra kết quả
if [ $? -eq 0 ]; then
    echo "Tạo tài khoản admin thành công!"
    echo "Bạn có thể đăng nhập với thông tin sau:"
    echo "Email: $EMAIL"
    echo "Mật khẩu: $PASSWORD"
else
    echo "Tạo tài khoản admin thất bại. Vui lòng kiểm tra lỗi ở trên."
fi
