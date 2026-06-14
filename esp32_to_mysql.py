import serial
import mysql.connector
import threading
import time
import re
from config import Config

# Cấu hình cổng COM (Hiện tại đang để giả lập, bạn sẽ sửa lại sau)
COM_LOADCELL = 'COM3'  # Thay bằng cổng COM của ESP32 Loadcell
COM_ENCODER  = 'COM4'  # Thay bằng cổng COM của ESP32 Encoder
BAUD_RATE    = 115200

def get_db_connection():
    """Hàm kết nối tới MySQL database"""
    return mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )

def get_active_session(cursor):
    """Tìm ID của phiên đo đang bấm 'Bắt đầu' trên giao diện Web"""
    cursor.execute("SELECT id FROM sessions WHERE status = 'active' ORDER BY started_at DESC LIMIT 1")
    row = cursor.fetchone()
    return row[0] if row else None

def read_loadcell_thread():
    """Luồng xử lý dữ liệu từ ESP32 Load cell"""
    print(f"[*] Đang lắng nghe cổng Loadcell ({COM_LOADCELL})...")
    try:
        ser = serial.Serial(COM_LOADCELL, BAUD_RATE, timeout=1)
        db = get_db_connection()
        cursor = db.cursor()
        
        while True:
            if ser.in_waiting:
                # Đọc dòng dữ liệu dạng: timestamp_ms,luc1_N,luc2_N
                line = ser.readline().decode('utf-8').strip()
                parts = line.split(',')
                
                if len(parts) == 3:
                    try:
                        ts_ms = float(parts[0])
                        f1 = float(parts[1])
                        f2 = float(parts[2])
                        ts_s = ts_ms / 1000.0 # Chuyển sang giây
                        
                        session_id = get_active_session(cursor)
                        if session_id:
                            sql = "INSERT INTO loadcell_data (session_id, timestamp_s, force1_N, force2_N) VALUES (%s, %s, %s, %s)"
                            cursor.execute(sql, (session_id, ts_s, f1, f2))
                            db.commit()
                            print(f"[Loadcell] Session {session_id} -> t: {ts_s}s, F1: {f1}N, F2: {f2}N")
                        else:
                            print("[Loadcell] Hệ thống đang bật nhưng chưa có phiên đo nào Active trên Web.")
                    except ValueError:
                        pass
            time.sleep(0.01)
    except Exception as e:
        print(f"[Lỗi Loadcell] Không thể kết nối hoặc mất tín hiệu cổng {COM_LOADCELL}: {e}")

def read_encoder_thread():
    """Luồng xử lý dữ liệu từ ESP32 Encoder"""
    print(f"[*] Đang lắng nghe cổng Encoder ({COM_ENCODER})...")
    try:
        ser = serial.Serial(COM_ENCODER, BAUD_RATE, timeout=1)
        db = get_db_connection()
        cursor = db.cursor()
        
        # Biến lưu thời gian bắt đầu nhận để tính timestamp_s tương đối
        start_time = time.time()
        
        while True:
            if ser.in_waiting:
                # Đọc dòng dữ liệu dạng: Góc: 180.0°
                line = ser.readline().decode('utf-8').strip()
                
                # Dùng Regex để tách lấy số góc quay
                match = re.search(r"Góc:\s*([+-]?\d+\.?\d*)", line)
                if match:
                    try:
                        angle = float(match.group(1))
                        ts_s = round(time.time() - start_time, 2)
                        
                        session_id = get_active_session(cursor)
                        if session_id:
                            sql = "INSERT INTO encoder_data (session_id, timestamp_s, angle_deg) VALUES (%s, %s, %s)"
                            cursor.execute(sql, (session_id, ts_s, angle))
                            db.commit()
                            print(f"[Encoder] Session {session_id} -> t: {ts_s}s, Góc: {angle}°")
                        else:
                            print("[Encoder] Đọc được góc nhưng chưa có phiên đo nào Active trên Web.")
                    except ValueError:
                        pass
            time.sleep(0.01)
    except Exception as e:
        print(f"[Lỗi Encoder] Không thể kết nối hoặc mất tín hiệu cổng {COM_ENCODER}: {e}")

if __name__ == "__main__":
    print("=== ĐANG KHỞI ĐỘNG PYTHON BRIDGE ===")
    
    # Tạo 2 luồng độc lập chạy song song
    t1 = threading.Thread(target=read_loadcell_thread, daemon=True)
    t2 = threading.Thread(target=read_encoder_thread, daemon=True)
    
    t1.start()
    t2.start()
    
    # Giữ cho chương trình chính không bị tắt
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Đã dừng Python Bridge.")