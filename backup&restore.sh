#!/bin/bash

# Thư mục lưu backup
BACKUP_DIR="/backups"

# Tạo thư mục backup nếu chưa có
mkdir -p $BACKUP_DIR/models
mkdir -p $BACKUP_DIR/logs

# Hàm backup
backup() {
    # Backup mô hình
    cp saved_models/*.h5 $BACKUP_DIR/models

    # Backup log
    cp logs/api_requests.log $BACKUP_DIR/logs

    # Ghi lại thời gian backup
    echo "Backup hoàn thành vào $(date)" >> $BACKUP_DIR/backup.log
    
    echo "Backup đã hoàn thành."
}

# Hàm khôi phục
restore() {
    # Khôi phục mô hình
    cp $BACKUP_DIR/models/*.h5 saved_models/

    # Khôi phục log
    cp $BACKUP_DIR/logs/api_requests.log logs/

    # Ghi lại thời gian khôi phục
    echo "Khôi phục hoàn thành vào $(date)" >> $BACKUP_DIR/restore.log
    
    echo "Khôi phục đã hoàn thành."
}

# Menu lựa chọn
echo "Chọn chức năng:"
echo "1. Backup"
echo "2. Khôi phục"
read -p "Nhập lựa chọn của bạn (1 hoặc 2): " choice

case $choice in
    1)
        backup
        ;;
    2)
        restore
        ;;
    *)
        echo "Lựa chọn không hợp lệ. Vui lòng chọn 1 hoặc 2."
        ;;
esac