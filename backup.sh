#!/bin/bash

# Thư mục lưu backup
BACKUP_DIR="/backups"

# Tạo thư mục backup nếu chưa có
mkdir -p $BACKUP_DIR/models
mkdir -p $BACKUP_DIR/logs

# Backup mô hình
cp saved_models/*.h5 $BACKUP_DIR/models

# Backup log
cp logs/api_requests.log $BACKUP_DIR/logs

# Ghi lại thời gian backup
echo "Backup hoàn thành vào $(date)" >> $BACKUP_DIR/backup.log
