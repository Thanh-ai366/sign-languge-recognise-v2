#!/bin/bash

# Thư mục backup
BACKUP_DIR="/backups"

# Khôi phục mô hình
cp $BACKUP_DIR/models/*.h5 saved_models/

# Khôi phục log
cp $BACKUP_DIR/logs/api_requests.log logs/

# Ghi lại thời gian khôi phục
echo "Khôi phục hoàn thành vào $(date)" >> $BACKUP_DIR/restore.log
