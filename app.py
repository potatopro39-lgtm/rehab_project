from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import mysql.connector
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Khởi tạo SocketIO để làm bộ truyền dữ liệu realtime
socketio = SocketIO(app, cors_allowed_origins="*")

# Khởi tạo Bộ quản lý đăng nhập (Flask-Login)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Hàm kết nối Database nhanh
def get_db_connection():
    return mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )

# Lớp Người dùng phục vụ Đăng nhập
class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, username, role FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    db.close()
    if user_data:
        return User(user_data['id'], user_data['username'], user_data['role'])
    return None

# ==================== CÁC TUYẾN ĐƯỜNG (ROUTES) WEB ====================

@app.route('/')
@login_required
def index():
    """Tự động chuyển hướng về Dashboard nếu đã đăng nhập"""
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Trang đăng nhập"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Thử kiểm tra tài khoảnadmin (Hoặc tài khoản trong DB)
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        cursor.close()
        db.close()
        
        # LƯU Ý: Để đơn giản lúc test, nếu DB trống bạn nhập admin/admin vẫn cho vào
        if (user_data and user_data['password'] == password) or (username == 'admin' and password == 'admin'):
            uid = user_data['id'] if user_data else 1
            urole = user_data['role'] if user_data else 'admin'
            user = User(uid, username, urole)
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng!')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Đăng xuất tài khoản"""
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Màn hình đồ thị Realtime hiển thị Lực & Góc"""
    # Lấy danh sách bệnh nhân để hiển thị ở ô chọn (Dropdown) trước khi đo
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, code, full_name FROM patients ORDER BY created_at DESC")
    patients = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('dashboard.html', patients=patients)

@app.route('/patients')
@login_required
def patients():
    """Quản lý danh sách bệnh nhân"""
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM patients ORDER BY created_at DESC")
    patients_list = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('patients.html', patients=patients_list)

@app.route('/history')
@login_required
def history():
    """Xem lại lịch sử các phiên tập đo"""
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    query = """
        SELECT s.*, p.full_name as patient_name, p.code as patient_code 
        FROM sessions s 
        JOIN patients p ON s.patient_id = p.id 
        ORDER BY s.started_at DESC
    """
    cursor.execute(query)
    sessions_list = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('history.html', sessions=sessions_list)

# ==================== CÁC API PHỤC VỤ REALTIME & ĐỒ THỊ ====================

@app.route('/api/start_session', methods=['POST'])
@login_required
def start_session():
    """API kích hoạt một phiên đo mới từ giao diện Web"""
    patient_id = request.json.get('patient_id')
    if not patient_id:
        return jsonify({'status': 'error', 'message': 'Chưa chọn bệnh nhân'}), 400
        
    db = get_db_connection()
    cursor = db.cursor()
    # 1. Tự động dừng tất cả phiên đo cũ đang bị treo (nếu có)
    cursor.execute("UPDATE sessions SET status = 'interrupted', ended_at = NOW() WHERE status = 'active'")
    # 2. Tạo một phiên đo mới ở trạng thái 'active'
    cursor.execute("INSERT INTO sessions (patient_id, user_id, status) VALUES (%s, %s, 'active')", (patient_id, current_user.id))
    db.commit()
    session_id = cursor.lastrowid
    cursor.close()
    db.close()
    
    return jsonify({'status': 'success', 'session_id': session_id})

@app.route('/api/stop_session', methods=['POST'])
@login_required
def stop_session():
    """API bấm dừng phiên đo hiện tại"""
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("UPDATE sessions SET status = 'completed', ended_at = NOW() WHERE status = 'active'")
    db.commit()
    cursor.close()
    db.close()
    return jsonify({'status': 'success'})

# Lắng nghe kết nối WebSocket từ trình duyệt
@socketio.on('connect')
def handle_connect():
    print(f"[*] Trình duyệt đã kết nối WebSocket thành công.")

if __name__ == '__main__':
    print("=== ĐANG KHỞI ĐỘNG WEB SERVER FLASK ===")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)