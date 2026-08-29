"""
KUKA KRC5 Controller EthernetKRL (EKI) Interface Server Emulator
Standard: DIN EN ISO 10218-1 / KUKA System Software 8.7+ EKI Protocol
Industrial automated server simulating robot kinematics, safety relays, and TCP state.
"""

from __future__ import annotations

import datetime
import logging
import os
import re
import socket
import sys
from typing import Dict, Any

# Configure industrial standard logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("KUKA.KRC5.EKI")

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

HOST: str = "127.0.0.1"
PORT: int = 59152

current_pos: Dict[str, float] = {"X": 460.0, "Y": 0.0, "Z": 850.0}
is_powered_on: bool = True


def print_startup_banner() -> None:
    """Print industrial corporate startup diagnostics."""
    divider = "=" * 74
    print(divider)
    print("  KUKA Roboter GmbH | KRC5 Cyber-Physical Controller Simulator")
    print("  Protocol: EthernetKRL (EKI) XML v2.4 | Safety Standard: IEC 62061 / SIL 3")
    print(divider)
    print(f"[NET] Binding TCP socket listener to {HOST}:{PORT}...")
    print(f"[SYS] Initial Kinematic Position: X={current_pos['X']:.1f}mm, Y={current_pos['Y']:.1f}mm, Z={current_pos['Z']:.1f}mm")
    print("[SYS] 400V Main Drive Power: [ENERGIZED / READY]")
    print("[SYS] Awaiting incoming client connection & XML motion packets...\n")


def run_server() -> None:
    """Execute industrial socket server listening for KUKA XML payloads."""
    global is_powered_on
    print_startup_banner()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server_sock.bind((HOST, PORT))
        except OSError as bind_err:
            logger.error(f"Socket bind failed on {HOST}:{PORT}: {bind_err}")
            sys.exit(1)

        server_sock.listen()
        logger.info(f"KRC5 EKI listener established on port {PORT}")

        while True:
            conn, addr = server_sock.accept()
            with conn:
                try:
                    data = conn.recv(1024).decode('utf-8')
                except Exception as recv_err:
                    logger.warning(f"Connection read error from {addr}: {recv_err}")
                    continue

                if not data:
                    continue

                ts = datetime.datetime.now().strftime("%H:%M:%S")
                raw_payload = data.strip()

                # 1. Reset / Safety Circuit Interlock Command
                if "<Reset>" in raw_payload or "<PowerOn>" in raw_payload:
                    is_powered_on = True
                    logger.info(f"[{ts}] [SAFETY-RELAY] Safety interlock reset. 400V main drives ENERGIZED.")
                    conn.sendall(b"<Robot><Status>ONLINE</Status><Drives>ENERGIZED</Drives></Robot>\n")
                    continue

                # 2. Halt / E-Stop Command
                x_match = re.search(r"<X>(.*?)</X>", raw_payload)
                y_match = re.search(r"<Y>(.*?)</Y>", raw_payload)
                z_match = re.search(r"<Z>(.*?)</Z>", raw_payload)

                if (z_match and float(z_match.group(1)) == -1.0) or "<Halt>" in raw_payload or "<EStop>" in raw_payload:
                    is_powered_on = False
                    logger.warning(f"[{ts}] [SAFETY-STOP] EMERGENCY STOP: 400V power cut, mechanical brakes locked.")
                    conn.sendall(b"<Robot><Status>POWERED_OFF</Status><Drives>DISENGAGED</Drives></Robot>\n")
                    continue

                # 3. Motion Target Check
                if x_match and y_match and z_match:
                    if not is_powered_on:
                        logger.warning(f"[{ts}] [MOTION-REJECTED] Motion disallowed while drives are de-energized.")
                        conn.sendall(b"<Robot><Status>ERROR_DRIVES_OFF</Status></Robot>\n")
                        continue

                    tgt_x = float(x_match.group(1))
                    tgt_y = float(y_match.group(1))
                    tgt_z = float(z_match.group(1))

                    current_pos.update({"X": tgt_x, "Y": tgt_y, "Z": tgt_z})
                    logger.info(f"[{ts}] [TCP-MOVE] Target reached -> X:{tgt_x:7.1f} | Y:{tgt_y:7.1f} | Z:{tgt_z:7.1f}")

                    response = (
                        f"<Robot><Status>REACHED</Status>"
                        f"<Current><X>{tgt_x:.1f}</X><Y>{tgt_y:.1f}</Y><Z>{tgt_z:.1f}</Z></Current></Robot>\n"
                    )
                    conn.sendall(response.encode('utf-8'))
                else:
                    status_str = "ONLINE" if is_powered_on else "POWERED_OFF"
                    response = (
                        f"<Robot><Status>{status_str}</Status>"
                        f"<Current><X>{current_pos['X']:.1f}</X><Y>{current_pos['Y']:.1f}</Y><Z>{current_pos['Z']:.1f}</Z></Current></Robot>\n"
                    )
                    conn.sendall(response.encode('utf-8'))


if __name__ == "__main__":
    run_server()
