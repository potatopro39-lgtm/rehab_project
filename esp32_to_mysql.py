import serial
import mysql.connector
import threading
import time
import re
import socketio  # <-- add this import
from config import Config

COM_LOADCELL = 'COM9'   # your loadcell port
COM_ENCODER  = 'COM5'   # your encoder port
BAUD_RATE = 115200

# Connect to the Flask-SocketIO server running on app.py
sio = socketio.Client()

def connect_socketio():
    try:
        sio.connect('http://localhost:5000')
        print("[*] Đã kết nối WebSocket tới Flask server.")
    except Exception as e:
        print(f"[!] Không thể kết nối WebSocket: {e}")

def get_db_connection():
    return mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )

def read_loadcell_thread():
    print(f"[*] Đang lắng nghe cổng Loadcell ({COM_LOADCELL})...")
    try:
        ser = serial.Serial(COM_LOADCELL, BAUD_RATE, timeout=1)
        session_start_time = {}  # track start time per session

        while True:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8').strip()
                parts = line.split(',')
                if len(parts) == 3:
                    try:
                        f1 = float(parts[1])
                        f2 = float(parts[2])

                        db = get_db_connection()
                        cursor = db.cursor()
                        cursor.execute("SELECT id FROM sessions WHERE status = 'active' ORDER BY started_at DESC LIMIT 1")
                        row = cursor.fetchone()
                        session_id = row[0] if row else None

                        if session_id:
                            # Start timer fresh when a new session is detected
                            if session_id not in session_start_time:
                                session_start_time = {session_id: time.time()}

                            ts_s = round(time.time() - session_start_time[session_id], 2)

                            sql = "INSERT INTO loadcell_data (session_id, timestamp_s, force1_N, force2_N) VALUES (%s, %s, %s, %s)"
                            cursor.execute(sql, (session_id, ts_s, f1, f2))
                            db.commit()
                            print(f"[Loadcell] Session {session_id} -> t: {ts_s}s, F1: {f1}N, F2: {f2}N")

                            sio.emit('new_data', {
                                'type': 'loadcell',
                                'time': ts_s,
                                'f1': f1,
                                'f2': f2
                            })
                        else:
                            print("[Loadcell] Chưa có phiên đo nào Active trên Web.")
                            session_start_time = {}

                        cursor.close()
                        db.close()
                    except ValueError:
                        pass
            time.sleep(0.01)
    except Exception as e:
        print(f"[Lỗi Loadcell] Không thể kết nối hoặc mất tín hiệu cổng {COM_LOADCELL}: {e}")

def read_encoder_thread():
    print(f"[*] Đang lắng nghe cổng Encoder ({COM_ENCODER})...")
    try:
        ser = serial.Serial(COM_ENCODER, BAUD_RATE, timeout=1)
        session_start_time = {}  # track start time per session

        while True:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8').strip()
                match = re.search(r"Góc:\s*([+-]?\d+\.?\d*)", line)
                if match:
                    try:
                        angle = float(match.group(1))

                        db = get_db_connection()
                        cursor = db.cursor()
                        cursor.execute("SELECT id FROM sessions WHERE status = 'active' ORDER BY started_at DESC LIMIT 1")
                        row = cursor.fetchone()
                        session_id = row[0] if row else None

                        if session_id:
                            # Start timer fresh when a new session is detected
                            if session_id not in session_start_time:
                                session_start_time = {session_id: time.time()}
                            
                            ts_s = round(time.time() - session_start_time[session_id], 2)

                            sql = "INSERT INTO encoder_data (session_id, timestamp_s, angle_deg) VALUES (%s, %s, %s)"
                            cursor.execute(sql, (session_id, ts_s, angle))
                            db.commit()
                            print(f"[Encoder] Session {session_id} -> t: {ts_s}s, Góc: {angle}°")

                            sio.emit('new_data', {
                                'type': 'encoder',
                                'time': ts_s,
                                'angle': angle
                            })
                        else:
                            print("[Encoder] Chưa có phiên đo nào Active trên Web.")
                            # Clear session timer when no active session
                            session_start_time = {}

                        cursor.close()
                        db.close()
                    except ValueError:
                        pass
            time.sleep(0.01)
    except Exception as e:
        print(f"[Lỗi Encoder] Không thể kết nối hoặc mất tín hiệu cổng {COM_ENCODER}: {e}")

if __name__ == "__main__":
    print("=== ĐANG KHỞI ĐỘNG PYTHON BRIDGE ===")
    
    connect_socketio()  # Connect to Flask first

    t1 = threading.Thread(target=read_loadcell_thread, daemon=True)
    t2 = threading.Thread(target=read_encoder_thread, daemon=True)
    t1.start()
    t2.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Đã dừng Python Bridge.")
        sio.disconnect()