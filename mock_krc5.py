import datetime
import os
import re
import socket
import sys
import time

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

HOST = "127.0.0.1"
PORT = 59152
current_pos = {"X": 460.0, "Y": 0.0, "Z": 850.0}
is_powered_on = True

def safe_print(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('ascii', 'replace').decode('ascii'))

safe_print("=" * 70)
safe_print("  [KUKA] VIRTUAL KRC5 CONTROLLER RUNNING (EKI INTERFACE EMULATOR)")
safe_print("=" * 70)
safe_print(f"[*] Binding network listener to {HOST}:{PORT}...")
safe_print(f"[*] Initial Robot Position -> X: {current_pos['X']}mm | Y: {current_pos['Y']}mm | Z: {current_pos['Z']}mm")
safe_print("[*] Drives Status: [ENERGIZED / READY]")
safe_print("[*] Ready and listening for motion commands & telemetry requests...\n")

def run_server():
    global is_powered_on
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            with conn:
                try:
                    data = conn.recv(1024).decode('utf-8')
                except Exception:
                    continue
                if not data:
                    continue

                ts = datetime.datetime.now().strftime("%H:%M:%S")
                raw_payload = data.strip()

                # 1. Reset / Power-On command
                if "<Reset>" in raw_payload or "<PowerOn>" in raw_payload:
                    is_powered_on = True
                    safe_print(f"[{ts}] [OK] SAFETY CIRCUIT RESET: Main contactors energized. Drives ONLINE.")
                    conn.sendall(b"<Robot><Status>ONLINE</Status><Drives>ENERGIZED</Drives></Robot>\n")
                    continue

                # 2. Halt / E-Stop Command
                x_m = re.search(r"<X>(.*?)</X>", raw_payload)
                y_m = re.search(r"<Y>(.*?)</Y>", raw_payload)
                z_m = re.search(r"<Z>(.*?)</Z>", raw_payload)

                if (z_m and float(z_m.group(1)) == -1.0) or "<Halt>" in raw_payload or "<EStop>" in raw_payload:
                    is_powered_on = False
                    safe_print(f"[{ts}] [STOP] EMERGENCY STOP: 400V power disengaged, brakes locked.")
                    conn.sendall(b"<Robot><Status>POWERED_OFF</Status><Drives>DISENGAGED</Drives></Robot>\n")
                    continue

                # 3. Motion Target Check
                if x_m and y_m and z_m:
                    if not is_powered_on:
                        safe_print(f"[{ts}] [REJECTED] Machine is POWERED OFF. Reset safety circuit first!")
                        conn.sendall(b"<Robot><Status>ERROR_DRIVES_OFF</Status></Robot>\n")
                        continue

                    tgt_x = float(x_m.group(1))
                    tgt_y = float(y_m.group(1))
                    tgt_z = float(z_m.group(1))

                    current_pos.update({"X": tgt_x, "Y": tgt_y, "Z": tgt_z})
                    safe_print(f"[{ts}] [TCP MOVE] -> X:{tgt_x:7.1f} | Y:{tgt_y:7.1f} | Z:{tgt_z:7.1f} [REACHED]")

                    response = f"<Robot><Status>REACHED</Status><Current><X>{tgt_x:.1f}</X><Y>{tgt_y:.1f}</Y><Z>{tgt_z:.1f}</Z></Current></Robot>\n"
                    conn.sendall(response.encode('utf-8'))
                else:
                    status_str = "ONLINE" if is_powered_on else "POWERED_OFF"
                    conn.sendall(f"<Robot><Status>{status_str}</Status><Current><X>{current_pos['X']:.1f}</X><Y>{current_pos['Y']:.1f}</Y><Z>{current_pos['Z']:.1f}</Z></Current></Robot>\n".encode('utf-8'))

if __name__ == "__main__":
    run_server()
