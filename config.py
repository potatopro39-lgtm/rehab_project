import os

class Config:
    # Cấu hình kết nối MySQL (Mặc định của XAMPP)
    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_PASSWORD = ''  # XAMPP mặc định để mật khẩu trống
    DB_NAME = 'rehab_db'
    
    # Cấu hình bảo mật cho Flask Web Server
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'rehab_secret_key_123'
    
    # Cấu hình gửi Email thông báo (Sẽ điền thông số sau khi làm đến phần gửi mail)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'your_email@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'your_app_password'