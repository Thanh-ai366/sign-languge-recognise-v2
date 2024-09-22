from datetime import datetime, timedelta
import redis

# Khởi tạo Redis để lưu trữ token blacklist
r = redis.Redis(host='localhost', port=6379, db=0)

# Thêm token vào blacklist
def blacklist_token(jti):
    r.set(jti, 'blacklisted', ex=timedelta(hours=1))

# Kiểm tra xem token có trong blacklist không
def is_token_blacklisted(jti):
    return r.get(jti) is not None
