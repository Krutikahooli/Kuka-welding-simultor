"""
KUKA KRC5 Industrial Robotic Weld Cell Controller
HMI & 3D Cyber-Physical Digital Twin Interface

Industrial Standard: DIN EN ISO 10218-1 / IEC 62061 SIL 3 / EN ISO 13849-1 Cat. 4
Architecture: Modular Componentized MVC with Real-Time Kinematics & EKI Socket Interface
"""

from __future__ import annotations

import logging
import math
import os
import platform
import random
import socket
import struct
import subprocess
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Dict, List, Optional, Tuple, Union

# Configure enterprise standard logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("KUKA.HMI")

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Platform Sound Capabilities
SYSTEM_OS = platform.system().lower()
HAS_WINSOUND = False
if SYSTEM_OS == "windows":
    try:
        import winsound
        HAS_WINSOUND = True
    except ImportError:
        HAS_WINSOUND = False

KUKA_IP: str = "127.0.0.1"
KUKA_PORT: int = 59152
BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
SOUND_FILE: str = os.path.join(BASE_DIR, "weld_sound.wav")
SHUTDOWN_SOUND: str = os.path.join(BASE_DIR, "estop_sound.wav")


# ==============================================================================
# 1. INDUSTRIAL METALLURGY SPECIFICATIONS & PROCESS PARAMETERS
# ==============================================================================
METALS_DATABASE: Dict[str, Dict[str, Any]] = {
    'carbon_steel': {
        'name': 'Mild Carbon Steel (AWS A36 / DIN 17100)',
        'code': 'A36 Structural Carbon Steel',
        'standard': 'AWS D1.1 / ISO 15614-1',
        'pipe_base': '#334155',
        'pipe_body': '#475569',
        'pipe_highlight': '#64748b',
        'seam_col': '#ff5500',
        'bead_col': '#f59e0b',
        'bead_outline': '#ea580c',
        'gas': '82% Ar / 18% CO2',
        'voltage': 24.2,
        'current': 185.0,
        'wire_speed': 8.4,
        'spark_colors': ['#ffffff', '#fbbf24', '#f97316', '#ffedd5'],
        'arc_core': '#ffffff',
        'arc_glow': '#00e5ff',
        'desc': 'Standard structural carbon steel. High penetration, warm amber weld bead deposit.'
    },
    'stainless_316l': {
        'name': 'Stainless Steel (AISI 316L / DIN 1.4404)',
        'code': '316L Austenitic Stainless',
        'standard': 'AWS D1.6 / ISO 3581',
        'pipe_base': '#64748b',
        'pipe_body': '#94a3b8',
        'pipe_highlight': '#f1f5f9',
        'seam_col': '#d97706',
        'bead_col': '#fbbf24',
        'bead_outline': '#b45309',
        'gas': '98% Ar / 2% CO2',
        'voltage': 22.8,
        'current': 165.0,
        'wire_speed': 7.2,
        'spark_colors': ['#ffffff', '#38bdf8', '#fbbf24', '#f8fafc'],
        'arc_core': '#ffffff',
        'arc_glow': '#38bdf8',
        'desc': 'Corrosion resistant marine alloy. Bright metallic silver sheen with gold/purple HAZ oxidation.'
    },
    'aluminum_6061': {
        'name': 'Aluminum Alloy (AA 6061-T6)',
        'code': '6061-T6 Aerospace Aluminum',
        'standard': 'AWS D1.2 / EN ISO 18273',
        'pipe_base': '#94a3b8',
        'pipe_body': '#cbd5e1',
        'pipe_highlight': '#ffffff',
        'seam_col': '#0284c7',
        'bead_col': '#e2e8f0',
        'bead_outline': '#94a3b8',
        'gas': '100% Pure Argon (Ar)',
        'voltage': 21.5,
        'current': 210.0,
        'wire_speed': 11.8,
        'spark_colors': ['#ffffff', '#00f2fe', '#e0f2fe', '#ffffff'],
        'arc_core': '#ffffff',
        'arc_glow': '#00f2fe',
        'desc': 'High thermal conductivity aluminum. Frosted pearl-silver weld bead with clean AC arc.'
    },
    'titanium_gr5': {
        'name': 'Titanium Alloy (Grade 5 Ti-6Al-4V)',
        'code': 'Grade 5 Titanium (Ti-6Al-4V)',
        'standard': 'AMS 4911 / AWS D1.9',
        'pipe_base': '#475569',
        'pipe_body': '#64748b',
        'pipe_highlight': '#94a3b8',
        'seam_col': '#8b5cf6',
        'bead_col': '#c084fc',
        'bead_outline': '#7c3aed',
        'gas': '99.999% High-Purity Argon',
        'voltage': 19.5,
        'current': 140.0,
        'wire_speed': 5.8,
        'spark_colors': ['#ffffff', '#c084fc', '#67e8f9', '#fdf4ff'],
        'arc_core': '#ffffff',
        'arc_glow': '#a855f7',
        'desc': 'Aerospace superalloy. Vibrant rainbow anodization heat tint (straw, purple, royal blue).'
    },
    'copper_brass': {
        'name': 'Free-Machining Brass (UNS C36000)',
        'code': 'C360 Naval Brass / Copper',
        'standard': 'ASTM B16 / AWS C5.5',
        'pipe_base': '#78350f',
        'pipe_body': '#b45309',
        'pipe_highlight': '#f59e0b',
        'seam_col': '#ea580c',
        'bead_col': '#f59e0b',
        'bead_outline': '#9a3412',
        'gas': '75% Argon / 25% Helium',
        'voltage': 26.5,
        'current': 230.0,
        'wire_speed': 9.8,
        'spark_colors': ['#ffffff', '#fb923c', '#f59e0b', '#fef08a'],
        'arc_core': '#ffffff',
        'arc_glow': '#f97316',
        'desc': 'High electrical and thermal conductivity bronze. Warm golden-rose metallic deposit.'
    },
    'inconel_718': {
        'name': 'Inconel 718 Nickel Superalloy (UNS N07718)',
        'code': 'Inconel 718 Nickel-Chromium',
        'standard': 'AMS 5596 / AWS D1.8',
        'pipe_base': '#3f3f46',
        'pipe_body': '#52525b',
        'pipe_highlight': '#a1a1aa',
        'seam_col': '#d97706',
        'bead_col': '#eab308',
        'bead_outline': '#854d0e',
        'gas': '95% Ar / 5% H2',
        'voltage': 23.5,
        'current': 155.0,
        'wire_speed': 6.5,
        'spark_colors': ['#ffffff', '#fde047', '#f59e0b', '#fafaf9'],
        'arc_core': '#ffffff',
        'arc_glow': '#eab308',
        'desc': 'Extreme temperature turbine superalloy. High strength champagne-gold bead deposit.'
    }
}


# ==============================================================================
# 2. AUDIO SYNTHESIS & CROSS-PLATFORM AUDIO CONTROLLER
# ==============================================================================
def generate_audio_assets() -> None:
    """Generate industrial sound assets if not present on disk."""
    import wave
    sample_rate = 22050

    if not os.path.exists(SOUND_FILE):
        try:
            with wave.open(SOUND_FILE, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                frames = bytearray()
                for i in range(int(sample_rate * 1.4)):
                    t = float(i) / sample_rate
                    hum = 0.28 * math.sin(2 * math.pi * 120 * t) + 0.16 * math.sin(2 * math.pi * 240 * t)
                    crackle = (random.random() * 2 - 1) * 0.40
                    if random.random() < 0.08:
                        crackle += (random.random() * 2 - 1) * 0.72
                    sample_val = max(-1.0, min(1.0, hum + crackle))
                    frames.extend(struct.pack('<h', int(sample_val * 26000)))
                wav_file.writeframes(frames)
        except Exception as err:
            logger.debug(f"Weld sound generation: {err}")

    if not os.path.exists(SHUTDOWN_SOUND):
        try:
            with wave.open(SHUTDOWN_SOUND, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                frames = bytearray()
                for i in range(int(sample_rate * 0.50)):
                    t = float(i) / sample_rate
                    freq = max(35.0, 340.0 * math.exp(-t * 9.0))
                    envelope = math.exp(-t * 7.5)
                    tone = math.sin(2 * math.pi * freq * t) * envelope * 0.75
                    clunk = (random.random() * 2 - 1) * math.exp(-t * 22.0) * 0.95
                    sample_val = max(-1.0, min(1.0, tone + clunk))
                    frames.extend(struct.pack('<h', int(sample_val * 28000)))
                wav_file.writeframes(frames)
        except Exception as err:
            logger.debug(f"EStop sound generation: {err}")


class SoundManager:
    """Industrial audio controller supporting Windows winsound and macOS/Linux subprocess."""
    def __init__(self):
        self.enabled: bool = True
        self.is_playing: bool = False
        self._proc: Optional[subprocess.Popen] = None

    def play_weld(self) -> None:
        if not self.enabled or self.is_playing:
            return
        self.is_playing = True
        if HAS_WINSOUND:
            try:
                winsound.PlaySound(SOUND_FILE, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
            except Exception:
                self.is_playing = False
        elif SYSTEM_OS == "darwin" and os.path.exists(SOUND_FILE):
            try:
                self._proc = subprocess.Popen(["afplay", SOUND_FILE], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                self.is_playing = False

    def stop_weld(self) -> None:
        if not self.is_playing:
            return
        self.is_playing = False
        if HAS_WINSOUND:
            try:
                winsound.PlaySound(None, winsound.SND_PURGE)
            except Exception:
                pass
        elif self._proc:
            try:
                self._proc.terminate()
                self._proc = None
            except Exception:
                pass

    def play_estop(self) -> None:
        if not self.enabled:
            return
        if HAS_WINSOUND:
            try:
                winsound.PlaySound(SHUTDOWN_SOUND, winsound.SND_FILENAME | winsound.SND_ASYNC)
            except Exception:
                pass
        elif SYSTEM_OS == "darwin" and os.path.exists(SHUTDOWN_SOUND):
            try:
                subprocess.Popen(["afplay", SHUTDOWN_SOUND], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass


# ==============================================================================
# 3. KINEMATICS ENGINE (6-AXIS ARTICULATED ARM)
# ==============================================================================
class KinematicsEngine:
    """
    KUKA 6-Axis Industrial Robot Kinematics Solver.
    Preserves exact constant link lengths for standard 6-DOF industrial architecture.
    """
    def __init__(self):
        self.d1: float = 320.0     # Base height to A2 shoulder pivot
        self.a1: float = 140.0     # Shoulder horizontal offset from A1 axis
        self.l1: float = 430.0     # Upper arm link (Shoulder A2 to Elbow A3)
        self.l2: float = 430.0     # Forearm link (Elbow A3 to Wrist Flange A5)
        self.l3: float = 140.0     # Tool Flange to Torch Tip (TCP)

        self.limits: Dict[str, Tuple[float, float]] = {
            'A1': (-185.0, 185.0),
            'A2': (-135.0, 45.0),
            'A3': (-120.0, 155.0),
            'A4': (-180.0, 180.0),
            'A5': (-125.0, 125.0),
            'A6': (-350.0, 350.0)
        }

    def solve(self, target_x: float, target_y: float, target_z: float) -> Tuple[Dict[str, Tuple[float, float, float]], Dict[str, float], bool]:
        tx = float(target_x)
        ty = float(target_y)
        tz = float(target_z)

        # 1. Base Axis A1
        a1_rad = math.atan2(ty, tx)
        a1_deg = math.degrees(a1_rad)
        ux = math.cos(a1_rad)
        uy = math.sin(a1_rad)
        r_xy = math.sqrt(tx * tx + ty * ty) + 1e-6

        # 2. Tool Vector & Wrist Center Point (W)
        t_pitch = math.radians(55.0)
        w_r = r_xy - self.l3 * math.sin(t_pitch)
        w_z = tz + self.l3 * math.cos(t_pitch)

        dr = w_r - self.a1
        dz = w_z - self.d1
        d_reach = math.sqrt(dr * dr + dz * dz)

        min_reach = abs(self.l1 - self.l2) + 5.0
        max_reach = self.l1 + self.l2 - 5.0
        reachable = (min_reach <= d_reach <= max_reach)
        d_clamped = max(min_reach, min(max_reach, d_reach))

        # Law of Cosines for Elbow and Shoulder
        cos_alpha = (self.l1 * self.l1 + d_clamped * d_clamped - self.l2 * self.l2) / (2.0 * self.l1 * d_clamped)
        alpha = math.acos(max(-1.0, min(1.0, cos_alpha)))
        phi = math.atan2(dz, dr)
        theta1 = phi + alpha

        cos_beta = (self.l1 * self.l1 + self.l2 * self.l2 - d_clamped * d_clamped) / (2.0 * self.l1 * self.l2)
        beta = math.acos(max(-1.0, min(1.0, cos_beta)))
        theta2 = math.pi - beta

        a2_deg = math.degrees(math.pi / 2.0 - theta1)
        a3_deg = math.degrees(theta2 - math.pi / 2.0)
        a5_deg = math.degrees(t_pitch - (theta1 - theta2))

        # Exact 3D Positions of all Joints
        j0 = (0.0, 0.0, 0.0)
        j1 = (0.0, 0.0, self.d1)
        j2 = (ux * self.a1, uy * self.a1, self.d1)

        r3 = self.a1 + self.l1 * math.cos(theta1)
        z3 = self.d1 + self.l1 * math.sin(theta1)
        j3 = (ux * r3, uy * r3, z3)

        r4 = r3 + self.l2 * math.cos(theta1 - theta2)
        z4 = z3 + self.l2 * math.sin(theta1 - theta2)
        j4 = (ux * r4, uy * r4, z4)

        tcp = (tx, ty, tz)

        joints = {'J0': j0, 'J1': j1, 'J2': j2, 'J3': j3, 'J4': j4, 'TCP': tcp}
        angles = {
            'A1': a1_deg,
            'A2': a2_deg,
            'A3': a3_deg,
            'A4': 0.0,
            'A5': a5_deg,
            'A6': (tx * 0.15 + ty * 0.1) % 360.0 - 180.0
        }
        return joints, angles, reachable


# ==============================================================================
# 4. KUKA INDUSTRIAL HMI CONTROLLER & CYBER-PHYSICAL WORKCELL UI
# ==============================================================================
class KukaVisualControlUI:
    """
    KUKA Roboter GmbH Enterprise smartHMI & 3D Digital Twin Application.
    Zero-emoji, high-contrast industrial control console.
    """
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("KUKA Roboter GmbH | KRC5 Cyber-Physical Controller | Industrial Workcell")
        self.root.geometry("1300x860")
        self.root.minsize(1100, 720)
        self.root.configure(bg="#07090e")

        try:
            generate_audio_assets()
        except Exception:
            pass

        self.sound = SoundManager()
        self.kinematics = KinematicsEngine()

        # Operational States
        self.curr_pos: Dict[str, float] = {"X": 460.0, "Y": 0.0, "Z": 850.0}
        self.disp_pos: Dict[str, float] = {"X": 460.0, "Y": 0.0, "Z": 850.0}
        self.target_pos: Dict[str, float] = {"X": 460.0, "Y": 0.0, "Z": 850.0}

        self.selected_metal_key = tk.StringVar(value='carbon_steel')
        self.is_powered_on: bool = True
        self.is_moving: bool = False
        self.is_welding: bool = False
        self.is_auto_cycle: bool = False
        self.connected: bool = False

        # Visual Toggles
        self.show_grid = tk.BooleanVar(value=True)
        self.show_trail = tk.BooleanVar(value=True)
        self.show_sparks = tk.BooleanVar(value=True)
        self.jog_step = tk.DoubleVar(value=25.0)
        self.speed_override = tk.IntVar(value=85)

        # 3D Orbit Camera State (Isometric default view)
        self.cam_azimuth: float = 38.0
        self.cam_elevation: float = 24.0
        self.cam_zoom: float = 1.15
        self.cam_pan_x: float = 0.0
        self.cam_pan_y: float = 0.0
        self._drag_start: Tuple[int, int] = (0, 0)

        self.path_history: List[Tuple[float, float, float]] = []
        self.weld_bead_history: List[Tuple[float, float, float]] = []
        self.particles: List[Dict[str, Any]] = []
        self.estop_flash_tick: int = 0
        self.arc_flash_tick: int = 0
        self.auto_step_name: str = "READY"

        self._init_styles()
        self._build_layout()
        self._bind_camera_events()
        self._start_animation_loop()
        self._test_connection_async()

    def _init_styles(self) -> None:
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.style.configure('.', background='#0c0f17', foreground='#e2e8f0')
        self.style.configure('TLabelframe', background='#111520', foreground='#ff5500', relief='solid', borderwidth=1)
        self.style.configure('TLabelframe.Label', background='#111520', foreground='#ff6a13', font=('Segoe UI', 9, 'bold'))
        self.style.configure('TLabel', background='#111520', foreground='#cbd5e1', font=('Segoe UI', 9))
        self.style.configure('TCheckbutton', background='#111520', foreground='#94a3b8', font=('Segoe UI', 8))
        self.style.map('TCheckbutton', foreground=[('active', '#38bdf8'), ('selected', '#38bdf8')])

        self.style.configure('TNotebook', background='#07090e', borderwidth=0)
        self.style.configure('TNotebook.Tab', background='#111520', foreground='#94a3b8', padding=[14, 7], font=('Segoe UI', 9, 'bold'))
        self.style.map('TNotebook.Tab', background=[('selected', '#1b2234')], foreground=[('selected', '#38bdf8')])

        self.style.configure('Primary.TButton', background='#ff5500', foreground='white', font=('Segoe UI', 9, 'bold'), borderwidth=0)
        self.style.map('Primary.TButton', background=[('active', '#ff7722'), ('disabled', '#262f40')])

        self.style.configure('Action.TButton', background='#0284c7', foreground='white', font=('Segoe UI', 9, 'bold'), borderwidth=0)
        self.style.map('Action.TButton', background=[('active', '#38bdf8'), ('disabled', '#1a2233')])

        self.style.configure('Halt.TButton', background='#dc2626', foreground='white', font=('Segoe UI', 10, 'bold'), borderwidth=0)
        self.style.map('Halt.TButton', background=[('active', '#ef4444')])

        self.style.configure('PowerOn.TButton', background='#16a34a', foreground='white', font=('Segoe UI', 10, 'bold'), borderwidth=0)
        self.style.map('PowerOn.TButton', background=[('active', '#22c55e')])

        self.style.configure('Jog.TButton', background='#171d2b', foreground='#60a5fa', font=('Segoe UI', 9, 'bold'), borderwidth=0)
        self.style.map('Jog.TButton', background=[('active', '#29334a'), ('disabled', '#10141e')])

        self.style.configure('Preset.TButton', background='#1a2333', foreground='#34d399', font=('Segoe UI', 8, 'bold'), borderwidth=0)
        self.style.map('Preset.TButton', background=[('active', '#2d3a52'), ('disabled', '#10141e')])

    def _build_layout(self) -> None:
        # 1. TOP HEADER & INDUSTRIAL TELEMETRY STATUS BAR
        hdr = tk.Frame(self.root, bg="#04060a", padx=16, pady=8)
        hdr.pack(fill='x')

        title_box = tk.Frame(hdr, bg="#04060a")
        title_box.pack(side='left')

        brand_chip = tk.Label(title_box, text="KUKA", bg="#ff5500", fg="#04060a", font=('Segoe UI', 11, 'bold'), padx=6, pady=1)
        brand_chip.pack(side='left', padx=(0, 8))

        tk.Label(title_box, text="KRC5 INDUSTRIAL ROBOTIC WELD CELL", bg="#04060a", fg="#f8fafc", font=('Segoe UI', 11, 'bold')).pack(side='left', padx=(2, 10))
        tk.Label(title_box, text="| Multi-Metal Metallurgy & Slotted Table Cell (KR 16 R2010-2)", bg="#04060a", fg="#64748b", font=('Segoe UI', 9)).pack(side='left')

        # Header Badges (Right)
        self.btn_sound = tk.Button(
            hdr, text="AUDIO: ON", bg="#141a27", fg="#38bdf8", activebackground="#212a3d",
            activeforeground="#ffffff", font=('Segoe UI', 8, 'bold'), relief='flat', padx=10, pady=3,
            command=self.toggle_sound
        )
        self.btn_sound.pack(side='right', padx=6)

        self.lbl_power_state = tk.Label(hdr, text="[400V DRIVES: ENERGIZED]", bg="#04060a", fg="#22c55e", font=('Consolas', 9, 'bold'))
        self.lbl_power_state.pack(side='right', padx=10)

        self.lbl_status = tk.Label(hdr, text="[LINK: CHECKING...]", bg="#04060a", fg="#f59e0b", font=('Consolas', 9, 'bold'))
        self.lbl_status.pack(side='right', padx=8)

        # 2. MAIN WORKSPACE SPLIT
        main_frame = tk.Frame(self.root, bg="#07090e")
        main_frame.pack(fill='both', expand=True, padx=8, pady=6)

        # LEFT: 3D VIEWPORT CANVAS
        left_box = tk.Frame(main_frame, bg="#111520", bd=1, relief='solid')
        left_box.pack(side='left', fill='both', expand=True, padx=(0, 6))

        # Viewport Header Toolbar
        vp_tool = tk.Frame(left_box, bg="#0a0e16", padx=10, pady=5)
        vp_tool.pack(fill='x')
        tk.Label(vp_tool, text="3D WORKCELL VIEWPORT | Left-Drag: Orbit | Scroll: Zoom | Right-Drag: Pan", bg="#0a0e16", fg="#94a3b8", font=('Segoe UI', 8)).pack(side='left')

        # Camera View presets
        btn_box = tk.Frame(vp_tool, bg="#0a0e16")
        btn_box.pack(side='right')
        for name, az, el in [("ISO", 38, 24), ("TOP", 0, 88), ("FRONT", 0, 4), ("SIDE", 90, 4)]:
            b = tk.Button(
                btn_box, text=name, bg="#141a27", fg="#38bdf8", activebackground="#222b3e",
                activeforeground="#ffffff", font=('Segoe UI', 8, 'bold'), relief='flat', padx=7, pady=1,
                command=lambda a=az, e=el: self.set_camera_preset(a, e)
            )
            b.pack(side='left', padx=2)

        # Options Checkboxes
        opt_box = tk.Frame(left_box, bg="#090c13", padx=8, pady=3)
        opt_box.pack(fill='x')
        ttk.Checkbutton(opt_box, text="Floor Grid", variable=self.show_grid, command=self._draw_scene).pack(side='left', padx=6)
        ttk.Checkbutton(opt_box, text="Toolpath Trail", variable=self.show_trail, command=self._draw_scene).pack(side='left', padx=6)
        ttk.Checkbutton(opt_box, text="Plasma Sparks", variable=self.show_sparks, command=self._draw_scene).pack(side='left', padx=6)

        self.lbl_cam_info = tk.Label(opt_box, text="Cam: Az=38° El=24° Zoom=1.15x", bg="#090c13", fg="#64748b", font=('Consolas', 8))
        self.lbl_cam_info.pack(side='right')

        # The 3D Canvas
        self.canvas = tk.Canvas(left_box, bg="#05070c", highlightthickness=0)
        self.canvas.pack(fill='both', expand=True, padx=2, pady=2)
        self.canvas.bind("<Configure>", lambda e: self._draw_scene())

        # RIGHT: TEACH PENDANT & METALLURGY DECK
        right_box = tk.Frame(main_frame, bg="#07090e", width=460)
        right_box.pack(side='right', fill='both', padx=(6, 0))
        right_box.pack_propagate(False)

        self.notebook = ttk.Notebook(right_box)
        self.notebook.pack(fill='both', expand=True)

        tab_motion = tk.Frame(self.notebook, bg="#0c0f17", padx=8, pady=8)
        tab_materials = tk.Frame(self.notebook, bg="#0c0f17", padx=8, pady=8)
        tab_telemetry = tk.Frame(self.notebook, bg="#0c0f17", padx=8, pady=8)

        self.notebook.add(tab_motion, text=" MOTION & JOG ")
        self.notebook.add(tab_materials, text=" METALLURGY & MATERIALS ")
        self.notebook.add(tab_telemetry, text=" DIAGNOSTICS & TELEMETRY ")

        self._build_tab_telemetry(tab_telemetry)
        self._build_tab_materials(tab_materials)
        self._build_tab_motion(tab_motion)

    def _build_tab_motion(self, parent: tk.Frame) -> None:
        # 1. Target Coordinates Frame
        f_coord = ttk.LabelFrame(parent, text=" Target Position (World TCP - mm) ", padding=8)
        f_coord.pack(fill='x', pady=(0, 4))

        grid = tk.Frame(f_coord, bg="#111520")
        grid.pack(fill='x')

        self.entries: Dict[str, tk.Entry] = {}
        for idx, (axis, def_val, clr) in enumerate([("X", "460.0", "#ef4444"), ("Y", "0.0", "#22c55e"), ("Z", "850.0", "#38bdf8")]):
            tk.Label(grid, text=f"{axis}:", bg="#111520", fg=clr, font=('Segoe UI', 10, 'bold'), width=3, anchor='e').grid(row=idx, column=0, padx=2, pady=2)

            ent = tk.Entry(
                grid, width=9, bg="#06080e", fg="#00ffcc", insertbackground="#00ffcc",
                font=('Consolas', 11, 'bold'), relief='solid', bd=1, highlightthickness=1,
                highlightcolor="#38bdf8", highlightbackground="#242d3d"
            )
            ent.insert(0, def_val)
            ent.grid(row=idx, column=1, padx=4, pady=2)
            self.entries[axis] = ent

        self.sliders: Dict[str, tk.Scale] = {}
        s_ranges = {"X": (150, 950), "Y": (-550, 550), "Z": (150, 1250)}
        for idx, axis in enumerate(["X", "Y", "Z"]):
            low, high = s_ranges[axis]
            s = tk.Scale(
                grid, from_=low, to=high, orient='horizontal', bg="#111520", fg="#94a3b8",
                activebackground="#ff5500", troughcolor="#06080e", highlightthickness=0,
                bd=0, showvalue=0, command=lambda val, a=axis: self._on_slider_change(a, val)
            )
            s.set(float(self.entries[axis].get()))
            s.grid(row=idx, column=2, sticky='ew', padx=(6, 2))
            self.sliders[axis] = s
        grid.columnconfigure(2, weight=1)

        # 2. Micro-Jog Step Increments & Matrix
        f_jog = ttk.LabelFrame(parent, text=" Micro-Jog Cartesian Axes ", padding=6)
        f_jog.pack(fill='x', pady=4)

        f_step = tk.Frame(f_jog, bg="#111520")
        f_step.pack(fill='x', pady=(0, 4))
        tk.Label(f_step, text="Step Increment:", bg="#111520", fg="#94a3b8", font=('Segoe UI', 8, 'bold')).pack(side='left', padx=(0, 4))
        for step in [1.0, 10.0, 25.0, 50.0, 100.0]:
            r = tk.Radiobutton(
                f_step, text=f"{int(step)}mm", value=step, variable=self.jog_step,
                bg="#111520", fg="#cbd5e1", selectcolor="#1b2234", activebackground="#111520",
                activeforeground="#38bdf8", font=('Segoe UI', 8)
            )
            r.pack(side='left', padx=2)

        jf = tk.Frame(f_jog, bg="#111520")
        jf.pack(fill='x')

        self.jog_buttons: List[ttk.Button] = []
        jog_defs = [
            ("X- (Retract)", 'X', -1, 0, 0), ("X+ (Extend)", 'X', 1, 0, 1),
            ("Y- (Left)", 'Y', -1, 0, 2),    ("Y+ (Right)", 'Y', 1, 0, 3),
            ("Z- (Down)", 'Z', -1, 1, 0),    ("Z+ (Up)", 'Z', 1, 1, 1),
            ("Reset Camera", 'cam', 0, 1, 2),("Zero Y Axis", 'zero_y', 0, 1, 3)
        ]
        for label, axis, dir_mul, r, c in jog_defs:
            if axis in ['X', 'Y', 'Z']:
                cmd = lambda a=axis, d=dir_mul: self.jog_axis(a, d)
                btn_style = 'Jog.TButton'
            elif axis == 'cam':
                cmd = lambda: self.set_camera_preset(38, 24)
                btn_style = 'Preset.TButton'
            else:
                cmd = lambda: self.set_coords(self.disp_pos['X'], 0.0, self.disp_pos['Z'])
                btn_style = 'Preset.TButton'

            b = ttk.Button(jf, text=label, style=btn_style, command=cmd)
            b.grid(row=r, column=c, padx=2, pady=2, sticky='ew')
            self.jog_buttons.append(b)
        for col in range(4):
            jf.columnconfigure(col, weight=1)

        # 3. Workcell Presets
        f_presets = ttk.LabelFrame(parent, text=" Calibrated Workcell Presets ", padding=6)
        f_presets.pack(fill='x', pady=4)

        pf = tk.Frame(f_presets, bg="#111520")
        pf.pack(fill='x')
        presets = [
            ("P1: Standby Home", 460, 0, 850),
            ("P2: Approach Clearance", 580, -180, 580),
            ("P3: Seam Sector 0°", 580, -180, 495),
            ("P4: Seam Sector 90°", 580, 0, 495),
            ("P5: Seam Sector 180°", 580, 180, 495),
            ("P6: Torch Clean Station", 260, 380, 680)
        ]
        self.preset_btns: List[ttk.Button] = []
        for i, (name, px, py, pz) in enumerate(presets):
            btn = ttk.Button(pf, text=name, style='Preset.TButton', command=lambda x=px, y=py, z=pz: self.set_coords(x, y, z))
            btn.grid(row=i//3, column=i%3, padx=2, pady=2, sticky='ew')
            self.preset_btns.append(btn)
        for col in range(3):
            pf.columnconfigure(col, weight=1)

        # 4. Speed Override Slider
        f_spd = tk.Frame(parent, bg="#0c0f17")
        f_spd.pack(fill='x', pady=(4, 2))
        tk.Label(f_spd, text="Program Velocity Override ($OV_PRO):", bg="#0c0f17", fg="#94a3b8", font=('Segoe UI', 8, 'bold')).pack(side='left')
        self.lbl_spd = tk.Label(f_spd, text="85%", bg="#0c0f17", fg="#38bdf8", font=('Segoe UI', 8, 'bold'), width=5)
        self.lbl_spd.pack(side='right')

        spd_scale = tk.Scale(
            f_spd, from_=10, to=100, orient='horizontal', variable=self.speed_override,
            bg="#0c0f17", fg="#cbd5e1", activebackground="#ff5500", troughcolor="#06080e",
            highlightthickness=0, bd=0, showvalue=0, command=lambda v: self.lbl_spd.config(text=f"{v}%")
        )
        spd_scale.pack(fill='x', expand=True, padx=8)

        # 5. Action Triggers & Emergency Control
        f_act = tk.Frame(parent, bg="#0c0f17")
        f_act.pack(fill='x', pady=4)

        self.btn_move = ttk.Button(f_act, text="EXECUTE MOTION", style='Primary.TButton', command=self.send_move)
        self.btn_move.pack(side='left', fill='x', expand=True, padx=(0, 2))

        self.btn_auto = ttk.Button(f_act, text="AUTO WELD CYCLE", style='Action.TButton', command=self.toggle_auto_demo)
        self.btn_auto.pack(side='left', fill='x', expand=True, padx=2)

        self.btn_estop = ttk.Button(f_act, text="EMERGENCY STOP (E-STOP)", style='Halt.TButton', command=self.trigger_estop)
        self.btn_estop.pack(side='right', fill='x', expand=True, padx=(2, 0))

        # Reset & Power-On Bar
        self.reset_bar = tk.Frame(parent, bg="#0c0f17")
        self.btn_power_on = ttk.Button(
            self.reset_bar,
            text="RESET SAFETY INTERLOCKS & ENERGIZE DRIVES",
            style='PowerOn.TButton',
            command=self.reset_and_power_on
        )
        self.btn_power_on.pack(fill='x', expand=True, pady=2)

    def _build_tab_materials(self, parent: tk.Frame) -> None:
        f_mat = ttk.LabelFrame(parent, text=" Workpiece Metallurgy & Weld Process Standards ", padding=8)
        f_mat.pack(fill='both', expand=True)

        tk.Label(
            f_mat,
            text="Select an alloy profile to dynamically configure metallurgical parameters, shielding gas composition, and weld deposition aesthetics:",
            bg="#111520", fg="#94a3b8", font=('Segoe UI', 8), wraplength=410, justify='left'
        ).pack(anchor='w', pady=(0, 6))

        for key, data in METALS_DATABASE.items():
            btn = tk.Radiobutton(
                f_mat,
                text=data['name'],
                value=key,
                variable=self.selected_metal_key,
                bg="#161c2b",
                fg="#f1f5f9",
                selectcolor="#ff5500",
                activebackground="#222b40",
                activeforeground="#38bdf8",
                font=('Segoe UI', 9, 'bold'),
                indicatoron=0,
                padx=10,
                pady=6,
                relief='solid',
                bd=1,
                command=self._on_material_change
            )
            btn.pack(fill='x', pady=2)

        # Material Info Box
        self.f_mat_info = tk.Frame(f_mat, bg="#080b12", bd=1, relief='solid', padx=8, pady=6)
        self.f_mat_info.pack(fill='x', pady=(8, 0))

        self.lbl_mat_name = tk.Label(self.f_mat_info, text="", bg="#080b12", fg="#ff5500", font=('Segoe UI', 9, 'bold'))
        self.lbl_mat_name.pack(anchor='w')

        self.lbl_mat_desc = tk.Label(self.f_mat_info, text="", bg="#080b12", fg="#cbd5e1", font=('Segoe UI', 8), wraplength=400, justify='left')
        self.lbl_mat_desc.pack(anchor='w', pady=2)

        self.lbl_mat_gas = tk.Label(self.f_mat_info, text="", bg="#080b12", fg="#38bdf8", font=('Consolas', 8, 'bold'))
        self.lbl_mat_gas.pack(anchor='w')

        self._on_material_change()

    def _on_material_change(self) -> None:
        key = self.selected_metal_key.get()
        data = METALS_DATABASE.get(key, METALS_DATABASE['carbon_steel'])

        self.lbl_mat_name.config(text=f"Active Metallurgy: {data['code']} ({data['standard']})")
        self.lbl_mat_desc.config(text=data['desc'])
        self.lbl_mat_gas.config(text=f"Shield Gas: {data['gas']} | Arc Parameters: {data['voltage']}V / {data['current']}A | Wire Feed: {data['wire_speed']}m/min")
        self.add_log(f"[MATERIAL] Selected profile: {data['name']} [Gas: {data['gas']}]")
        self._draw_scene()

    def _build_tab_telemetry(self, parent: tk.Frame) -> None:
        # 1. Joint Angles Telemetry Gauges (A1..A6)
        f_joints = ttk.LabelFrame(parent, text=" Real-Time Axis Angles (Degrees) ", padding=8)
        f_joints.pack(fill='x', pady=(0, 4))

        self.lbl_joints: Dict[str, tk.Label] = {}
        self.prog_joints: Dict[str, ttk.Progressbar] = {}
        j_grid = tk.Frame(f_joints, bg="#111520")
        j_grid.pack(fill='x')

        for idx, ax in enumerate(['A1', 'A2', 'A3', 'A4', 'A5', 'A6']):
            min_l, max_l = self.kinematics.limits[ax]
            tk.Label(j_grid, text=f"{ax}:", bg="#111520", fg="#38bdf8", font=('Consolas', 9, 'bold'), width=4, anchor='e').grid(row=idx, column=0, padx=2, pady=1)

            val_lbl = tk.Label(j_grid, text="0.0°", bg="#111520", fg="#00ffcc", font=('Consolas', 9, 'bold'), width=8, anchor='w')
            val_lbl.grid(row=idx, column=1, padx=4, pady=1)
            self.lbl_joints[ax] = val_lbl

            p = ttk.Progressbar(j_grid, orient='horizontal', length=140, mode='determinate', maximum=max_l - min_l)
            p.grid(row=idx, column=2, sticky='ew', padx=4, pady=1)
            self.prog_joints[ax] = p
        j_grid.columnconfigure(2, weight=1)

        # 2. Process Telemetry Readout
        f_process = ttk.LabelFrame(parent, text=" Welding Power Source & Process Telemetry ", padding=6)
        f_process.pack(fill='x', pady=4)

        pf = tk.Frame(f_process, bg="#111520")
        pf.pack(fill='x')

        self.telemetry_labels: Dict[str, tk.Label] = {}
        telemetry_items = [
            ("Arc Voltage", "0.0 V", "#38bdf8"),
            ("Weld Current", "0.0 A", "#ff5500"),
            ("Wire Feed Speed", "0.0 m/min", "#22c55e"),
            ("Shield Gas Flow", "0.0 L/min", "#a855f7")
        ]
        for idx, (title, val, col) in enumerate(telemetry_items):
            box = tk.Frame(pf, bg="#080b12", bd=1, relief='solid', padx=6, pady=4)
            box.grid(row=idx//2, column=idx%2, padx=3, pady=3, sticky='nsew')
            tk.Label(box, text=title, bg="#080b12", fg="#94a3b8", font=('Segoe UI', 8)).pack(anchor='w')
            lbl = tk.Label(box, text=val, bg="#080b12", fg=col, font=('Consolas', 11, 'bold'))
            lbl.pack(anchor='e')
            self.telemetry_labels[title] = lbl
        pf.columnconfigure(0, weight=1); pf.columnconfigure(1, weight=1)

        # 3. KRL Protocol Log Stream
        f_log = ttk.LabelFrame(parent, text=" KRL Communication Console & Diagnostics Log ", padding=4)
        f_log.pack(fill='both', expand=True, pady=(4, 0))

        self.txt_log = tk.Text(f_log, wrap='word', height=7, bg="#05070c", fg="#10b981", font=('Consolas', 8), bd=0)
        self.txt_log.pack(fill='both', expand=True)

        self.add_log("[SYS-INIT] KUKA KRC5 Cyber-Physical Controller initialized.")
        self.add_log("[SYS-INIT] 6-Axis Kinematics Engine active. Ready for commands.")

    def _bind_camera_events(self) -> None:
        self.canvas.bind("<Button-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag_orbit)
        self.canvas.bind("<Button-3>", self._on_mouse_down)
        self.canvas.bind("<B3-Motion>", self._on_mouse_drag_pan)
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        self.canvas.bind("<Button-4>", lambda e: self._adjust_zoom(1.1))
        self.canvas.bind("<Button-5>", lambda e: self._adjust_zoom(0.9))
        self.canvas.bind("<Double-Button-1>", lambda e: self.set_camera_preset(38, 24))

    def _on_mouse_down(self, event: tk.Event) -> None:
        self._drag_start = (event.x, event.y)

    def _on_mouse_drag_orbit(self, event: tk.Event) -> None:
        dx = event.x - self._drag_start[0]
        dy = event.y - self._drag_start[1]
        self._drag_start = (event.x, event.y)

        self.cam_azimuth = (self.cam_azimuth + dx * 0.5) % 360.0
        self.cam_elevation = max(2.0, min(89.0, self.cam_elevation - dy * 0.5))
        self.lbl_cam_info.config(text=f"Cam: Az={int(self.cam_azimuth)}° El={int(self.cam_elevation)}° Zoom={self.cam_zoom:.2f}x")
        self._draw_scene()

    def _on_mouse_drag_pan(self, event: tk.Event) -> None:
        dx = event.x - self._drag_start[0]
        dy = event.y - self._drag_start[1]
        self._drag_start = (event.x, event.y)

        self.cam_pan_x += dx
        self.cam_pan_y += dy
        self._draw_scene()

    def _on_mouse_wheel(self, event: tk.Event) -> None:
        factor = 1.1 if event.delta > 0 else 0.9
        self._adjust_zoom(factor)

    def _adjust_zoom(self, factor: float) -> None:
        self.cam_zoom = max(0.4, min(3.5, self.cam_zoom * factor))
        self.lbl_cam_info.config(text=f"Cam: Az={int(self.cam_azimuth)}° El={int(self.cam_elevation)}° Zoom={self.cam_zoom:.2f}x")
        self._draw_scene()

    def set_camera_preset(self, az: float, el: float) -> None:
        self.cam_azimuth = float(az)
        self.cam_elevation = float(el)
        self.cam_pan_x = 0.0
        self.cam_pan_y = 0.0
        self.cam_zoom = 1.15
        self.lbl_cam_info.config(text=f"Cam: Az={int(self.cam_azimuth)}° El={int(self.cam_elevation)}° Zoom={self.cam_zoom:.2f}x")
        self._draw_scene()

    def set_coords(self, x: float, y: float, z: float) -> None:
        self.entries['X'].delete(0, tk.END); self.entries['X'].insert(0, f"{x:.1f}")
        self.entries['Y'].delete(0, tk.END); self.entries['Y'].insert(0, f"{y:.1f}")
        self.entries['Z'].delete(0, tk.END); self.entries['Z'].insert(0, f"{z:.1f}")

        for ax, val in [('X', x), ('Y', y), ('Z', z)]:
            if ax in self.sliders:
                self.sliders[ax].set(val)
        self.send_move()

    def _on_slider_change(self, axis: str, val: Union[float, str]) -> None:
        self.entries[axis].delete(0, tk.END)
        self.entries[axis].insert(0, f"{float(val):.1f}")
        if not self.is_moving:
            self.send_move()

    def jog_axis(self, axis: str, dir_mul: int) -> None:
        if not self.is_powered_on:
            return
        step = self.jog_step.get()
        try:
            curr = float(self.entries[axis].get())
            new_val = curr + (dir_mul * step)
            self.entries[axis].delete(0, tk.END)
            self.entries[axis].insert(0, f"{new_val:.1f}")
            if axis in self.sliders:
                self.sliders[axis].set(new_val)
            self.send_move()
        except ValueError:
            pass

    def add_log(self, msg: str) -> None:
        logger.info(msg)
        if hasattr(self, 'txt_log'):
            try:
                self.txt_log.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
                self.txt_log.see(tk.END)
            except Exception:
                pass

    def toggle_sound(self) -> None:
        self.sound.enabled = not self.sound.enabled
        if self.sound.enabled:
            self.btn_sound.config(text="AUDIO: ON", fg="#38bdf8")
            self.add_log("[AUDIO] Sound effects enabled.")
        else:
            self.btn_sound.config(text="AUDIO: MUTED", fg="#94a3b8")
            self.sound.stop_weld()
            self.add_log("[AUDIO] Sound effects muted.")

    def trigger_estop(self) -> None:
        self.is_powered_on = False
        self.is_auto_cycle = False
        self.is_welding = False
        self.is_moving = False
        self.auto_step_name = "E-STOPPED"

        self.sound.stop_weld()
        self.sound.play_estop()

        self.btn_auto.config(text="AUTO WELD CYCLE")
        self.lbl_power_state.config(text="[400V DRIVES: LOCKED (E-STOP)]", fg="#ef4444")
        self.reset_bar.pack(fill='x', pady=(4, 0), before=self.btn_estop.master)
        self._set_controls_state('disabled')
        self.add_log("[SAFETY-ESTOP] Emergency Stop Engaged: 400V Main Contactors Open! Mechanical Brakes Clamped.")

        threading.Thread(target=self._tcp_send_packet, args=(0, 0, -1), daemon=True).start()

    def reset_and_power_on(self) -> None:
        self.add_log("[SAFETY-RESET] Resetting safety interlocks and energizing drives...")

        def worker():
            packet = "<Robot><Command><Reset>1</Reset></Command></Robot>\n"
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(2.0)
                    s.connect((KUKA_IP, KUKA_PORT))
                    s.sendall(packet.encode('utf-8'))
                    res = s.recv(1024).decode('utf-8').strip()
                    self.root.after(0, lambda: self.add_log(f"[CONTROLLER-ACK] {res}"))
            except Exception as err:
                self.root.after(0, lambda: self.add_log(f"[LINK-NOTE] {err}"))

            def on_reboot():
                self.is_powered_on = True
                self.reset_bar.pack_forget()
                self.lbl_power_state.config(text="[400V DRIVES: ENERGIZED]", fg="#22c55e")
                self._set_controls_state('normal')
                self.auto_step_name = "READY"
                self.add_log("[SAFETY-OK] Main contactors energized. System ONLINE and ready.")

            self.root.after(0, on_reboot)

        threading.Thread(target=worker, daemon=True).start()

    def _set_controls_state(self, state: str) -> None:
        self.btn_move.config(state=state)
        self.btn_auto.config(state=state)
        for b in self.preset_btns:
            b.config(state=state)
        for b in self.jog_buttons:
            b.config(state=state)

    def _test_connection_async(self) -> None:
        def worker():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1.2)
                s.connect((KUKA_IP, KUKA_PORT))
                s.close()
                self.connected = True
                self.root.after(0, lambda: self.lbl_status.config(text="[CONTROLLER: ONLINE]", fg="#22c55e"))
                self.root.after(0, lambda: self.add_log("[NET-OK] Connected to KRC5 Controller emulator (127.0.0.1:59152)."))
            except Exception:
                self.connected = False
                self.root.after(0, lambda: self.lbl_status.config(text="[CONTROLLER: OFFLINE]", fg="#ef4444"))
                self.root.after(0, lambda: self.add_log("[NET-WARN] Controller link offline. Start mock_krc5.py emulator."))

        threading.Thread(target=worker, daemon=True).start()

    def send_move(self) -> None:
        if not self.is_powered_on:
            messagebox.showwarning("Interlock Tripped", "Cannot execute motion: 400V drives are de-energized. Reset E-Stop first.")
            return

        try:
            x = float(self.entries['X'].get())
            y = float(self.entries['Y'].get())
            z = float(self.entries['Z'].get())
        except ValueError:
            messagebox.showerror("Format Error", "Target coordinates must be valid floating-point numbers.")
            return

        self.target_pos = {"X": x, "Y": y, "Z": z}
        self.is_moving = True
        self.btn_move.config(state='disabled')
        self.add_log(f"[MOTION-CMD] World TCP Target -> X:{x:.1f} Y:{y:.1f} Z:{z:.1f}")

        threading.Thread(target=self._tcp_send_packet, args=(x, y, z), daemon=True).start()

    def toggle_auto_demo(self) -> None:
        if not self.is_powered_on:
            messagebox.showwarning("Interlock Tripped", "Cannot start cycle: 400V drives are de-energized.")
            return

        if self.is_auto_cycle:
            self.is_auto_cycle = False
            self.is_welding = False
            self.sound.stop_weld()
            self.auto_step_name = "HOME STANDBY"
            self.btn_auto.config(text="AUTO WELD CYCLE")
            self.add_log("[CYCLE-ABORT] Auto weld cycle stopped. Returning to Standby Home (460, 0, 850)...")
            self.set_coords(460, 0, 850)
        else:
            self.is_auto_cycle = True
            self.btn_auto.config(text="STOP CYCLE [RETURN HOME]")
            self.weld_bead_history.clear()
            self.add_log(f"[CYCLE-START] Initiating automated weld cycle on {self.selected_metal_key.get()}...")
            threading.Thread(target=self._auto_cycle_loop, daemon=True).start()

    def _auto_cycle_loop(self) -> None:
        cycle_steps = [
            ("1. Approach Clearance", 580, -180, 580, 1.2),
            ("2. Shield Gas Pre-flow", 580, -180, 495, 0.8),
            ("3. Arc Strike & Linear Seam Weld", 580, -90, 495, 1.4),
            ("3. Arc Strike & Linear Seam Weld", 580, 0, 495, 1.4),
            ("3. Arc Strike & Linear Seam Weld", 580, 90, 495, 1.4),
            ("4. Seam Finish / Crater Fill", 580, 180, 495, 1.2),
            ("5. Post-Flow & Torch Retract", 500, 180, 680, 1.0),
            ("6. Standby Home", 460, 0, 850, 1.2)
        ]
        idx = 0
        while self.is_auto_cycle and self.is_powered_on:
            name, px, py, pz, delay = cycle_steps[idx]
            self.auto_step_name = name
            self.root.after(0, lambda x=px, y=py, z=pz: self.set_coords(x, y, z))
            time.sleep(delay)
            idx = (idx + 1) % len(cycle_steps)

    def _tcp_send_packet(self, x: float, y: float, z: float) -> None:
        packet = f"<Robot><Command><X>{x}</X><Y>{y}</Y><Z>{z}</Z></Command></Robot>\n"
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2.5)
                s.connect((KUKA_IP, KUKA_PORT))
                s.sendall(packet.encode('utf-8'))
                res = s.recv(1024).decode('utf-8').strip()
                self.connected = True
                self.root.after(0, lambda: self.lbl_status.config(text="[CONTROLLER: ONLINE]", fg="#22c55e"))
                if z != -1 and self.is_powered_on:
                    self.curr_pos = {"X": x, "Y": y, "Z": z}
        except Exception:
            self.connected = False
            self.root.after(0, lambda: self.lbl_status.config(text="[CONTROLLER: OFFLINE]", fg="#ef4444"))
            if z != -1 and self.is_powered_on:
                self.curr_pos = {"X": x, "Y": y, "Z": z}
        finally:
            self.is_moving = False
            if self.is_powered_on:
                self.root.after(0, lambda: self.btn_move.config(state='normal'))

    def _spawn_weld_sparks(self, x: float, y: float, z: float, metal_data: Dict[str, Any]) -> None:
        if not self.is_powered_on or not self.show_sparks.get():
            return
        colors = metal_data.get('spark_colors', ['#ffffff', '#fbbf24', '#f97316'])
        for _ in range(3):
            self.particles.append({
                'x': x + random.uniform(-1.5, 1.5),
                'y': y + random.uniform(-1.5, 1.5),
                'z': z,
                'vx': random.uniform(-5, 5),
                'vy': random.uniform(-5, 5),
                'vz': random.uniform(3, 9),
                'life': 1.0,
                'color': random.choice(colors)
            })

    def _start_animation_loop(self) -> None:
        override = self.speed_override.get() / 100.0
        lerp_speed = (0.14 if self.is_powered_on else 0.05) * override

        dx = (self.curr_pos['X'] - self.disp_pos['X']) * lerp_speed
        dy = (self.curr_pos['Y'] - self.disp_pos['Y']) * lerp_speed
        dz = (self.curr_pos['Z'] - self.disp_pos['Z']) * lerp_speed

        self.disp_pos['X'] += dx
        self.disp_pos['Y'] += dy
        self.disp_pos['Z'] += dz

        # Check if at Pipe Seam on Table (Welding zone: Z <= 520, X in [530, 630], Y in [-200, 200])
        is_at_seam = (self.disp_pos['Z'] <= 520 and 530 <= self.disp_pos['X'] <= 630 and abs(self.disp_pos['Y']) <= 210 and self.is_powered_on)
        self.is_welding = is_at_seam

        metal_key = self.selected_metal_key.get()
        metal_data = METALS_DATABASE.get(metal_key, METALS_DATABASE['carbon_steel'])

        if is_at_seam:
            self.weld_bead_history.append((self.disp_pos['X'], self.disp_pos['Y'], self.disp_pos['Z'] - 4))
            if len(self.weld_bead_history) > 180:
                self.weld_bead_history.pop(0)
            self._spawn_weld_sparks(self.disp_pos['X'], self.disp_pos['Y'], self.disp_pos['Z'], metal_data)
            self.sound.play_weld()

            self.telemetry_labels['Arc Voltage'].config(text=f"{metal_data['voltage'] + random.uniform(-0.6, 0.6):.1f} V")
            self.telemetry_labels['Weld Current'].config(text=f"{metal_data['current'] + random.uniform(-5, 5):.1f} A")
            self.telemetry_labels['Wire Feed Speed'].config(text=f"{metal_data['wire_speed'] + random.uniform(-0.2, 0.2):.1f} m/min")
            self.telemetry_labels['Shield Gas Flow'].config(text="18.5 L/min")
        else:
            self.sound.stop_weld()
            self.telemetry_labels['Arc Voltage'].config(text="0.0 V")
            self.telemetry_labels['Weld Current'].config(text="0.0 A")
            self.telemetry_labels['Wire Feed Speed'].config(text="0.0 m/min")
            self.telemetry_labels['Shield Gas Flow'].config(text="0.0 L/min" if not self.is_auto_cycle else "2.0 L/min (Pre-Flow)")

        if self.is_powered_on and self.show_trail.get() and (abs(dx) > 0.04 or abs(dy) > 0.04 or abs(dz) > 0.04):
            self.path_history.append((self.disp_pos['X'], self.disp_pos['Y'], self.disp_pos['Z']))
            if len(self.path_history) > 50:
                self.path_history.pop(0)

        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['z'] += p['vz']
            p['vz'] -= 1.2
            if p['z'] <= 380 and p['vz'] < 0:
                p['vz'] = -p['vz'] * 0.3
                p['vx'] *= 0.5
                p['vy'] *= 0.5
            p['life'] -= 0.12
        self.particles = [p for p in self.particles if p['life'] > 0]

        joints, angles, reachable = self.kinematics.solve(self.disp_pos['X'], self.disp_pos['Y'], self.disp_pos['Z'])
        for ax in ['A1', 'A2', 'A3', 'A4', 'A5', 'A6']:
            ang = angles[ax]
            self.lbl_joints[ax].config(text=f"{ang:6.1f}°")
            min_l, max_l = self.kinematics.limits[ax]
            clamped = max(min_l, min(max_l, ang))
            self.prog_joints[ax]['value'] = clamped - min_l

        self.arc_flash_tick = (self.arc_flash_tick + 1) % 6
        self.estop_flash_tick = (self.estop_flash_tick + 1) % 16

        self._draw_scene(joints=joints, reachable=reachable, metal_data=metal_data)
        self.root.after(30, self._start_animation_loop)

    # ==========================================================================
    # 5. 3D PROJECTION & CAD-GRADE RENDERING PIPELINE
    # ==========================================================================
    def _project_point(self, x: float, y: float, z: float, origin_x: float, origin_y: float, scale: float) -> Tuple[float, float, float]:
        az_rad = math.radians(-self.cam_azimuth)
        x1 = x * math.cos(az_rad) - y * math.sin(az_rad)
        y1 = x * math.sin(az_rad) + y * math.cos(az_rad)

        el_rad = math.radians(-self.cam_elevation)
        y2 = y1 * math.cos(el_rad) - z * math.sin(el_rad)
        z2 = y1 * math.sin(el_rad) + z * math.cos(el_rad)

        px = origin_x + self.cam_pan_x + x1 * scale * self.cam_zoom
        py = origin_y + self.cam_pan_y - z2 * scale * self.cam_zoom
        depth = y2
        return px, py, depth

    def _draw_scene(self, joints=None, reachable=True, metal_data=None) -> None:
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 50 or h < 50:
            return

        self.canvas.delete("all")

        ox = int(w * 0.44)
        oy = int(h * 0.72)
        scale = min(w, h) / 1850.0

        def proj(x: float, y: float, z: float) -> Tuple[float, float]:
            px, py, _ = self._project_point(x, y, z, ox, oy, scale)
            return px, py

        if metal_data is None:
            metal_key = self.selected_metal_key.get()
            metal_data = METALS_DATABASE.get(metal_key, METALS_DATABASE['carbon_steel'])

        # ----------------------------------------------------------------------
        # 1. Industrial Cell Floor & Workcell Boundary Perimeter
        # ----------------------------------------------------------------------
        if self.show_grid.get():
            for gx in range(-800, 1001, 200):
                p1 = proj(gx, -800, 0); p2 = proj(gx, 800, 0)
                self.canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill="#0f1420", width=1)
            for gy in range(-800, 801, 200):
                p1 = proj(-800, gy, 0); p2 = proj(1000, gy, 0)
                self.canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill="#0f1420", width=1)

            zone_pts = [proj(-650, -650, 0), proj(950, -650, 0), proj(950, 650, 0), proj(-650, 650, 0)]
            flat_zone = [c for p in zone_pts for c in p]
            self.canvas.create_polygon(flat_zone, fill="", outline="#ca8a04", width=1, dash=(8, 4))

        # ----------------------------------------------------------------------
        # 2. Slotted Industrial Steel Welding Fixture Table (Z = 380 mm)
        # ----------------------------------------------------------------------
        tbl_x_min, tbl_x_max = 440, 720
        tbl_y_min, tbl_y_max = -260, 260
        tbl_z_top = 380

        # Ground Shadow beneath table
        sh_pts = [proj(tbl_x_min-20, tbl_y_min-20, 0), proj(tbl_x_max+20, tbl_y_min-20, 0),
                  proj(tbl_x_max+20, tbl_y_max+20, 0), proj(tbl_x_min-20, tbl_y_max+20, 0)]
        self.canvas.create_polygon([c for p in sh_pts for c in p], fill="#030509", outline="")

        # Table Tubular Steel Legs
        for lx, ly in [(tbl_x_min+25, tbl_y_min+25), (tbl_x_min+25, tbl_y_max-25), (tbl_x_max-25, tbl_y_min+25), (tbl_x_max-25, tbl_y_max-25)]:
            p_top = proj(lx, ly, tbl_z_top); p_bot = proj(lx, ly, 0)
            self.canvas.create_line(p_top[0], p_top[1], p_bot[0], p_bot[1], fill="#1e293b", width=8)
            self.canvas.create_line(p_top[0], p_top[1], p_bot[0], p_bot[1], fill="#334155", width=4)

        # 3D Solid Table Top Plinth
        t1 = proj(tbl_x_min, tbl_y_min, tbl_z_top)
        t2 = proj(tbl_x_max, tbl_y_min, tbl_z_top)
        t3 = proj(tbl_x_max, tbl_y_max, tbl_z_top)
        t4 = proj(tbl_x_min, tbl_y_max, tbl_z_top)
        t1_b = proj(tbl_x_min, tbl_y_min, tbl_z_top - 30)
        t2_b = proj(tbl_x_max, tbl_y_min, tbl_z_top - 30)
        t3_b = proj(tbl_x_max, tbl_y_max, tbl_z_top - 30)

        self.canvas.create_polygon(t1[0], t1[1], t2[0], t2[1], t2_b[0], t2_b[1], t1_b[0], t1_b[1], fill="#1e293b", outline="#475569")
        self.canvas.create_polygon(t2[0], t2[1], t3[0], t3[1], t3_b[0], t3_b[1], t2_b[0], t2_b[1], fill="#0f172a", outline="#475569")
        self.canvas.create_polygon(t1[0], t1[1], t2[0], t2[1], t3[0], t3[1], t4[0], t4[1], fill="#263143", outline="#64748b", width=2)

        # Table Fixture Matrix Grid Slots
        for sl_y in range(-200, 220, 65):
            sp1 = proj(tbl_x_min + 30, sl_y, tbl_z_top + 1); sp2 = proj(tbl_x_max - 30, sl_y, tbl_z_top + 1)
            self.canvas.create_line(sp1[0], sp1[1], sp2[0], sp2[1], fill="#171d2b", width=2)

        # ----------------------------------------------------------------------
        # 3. Dynamic Metal Workpiece: Pipe Spool Joint on V-Blocks
        # ----------------------------------------------------------------------
        pipe_x = 580
        pipe_y_start, pipe_y_end = -200, 200
        pipe_z_center = tbl_z_top + 65
        pipe_r = 44

        # V-Block Support Clamps
        for v_y in [-160, 160]:
            vb1 = proj(pipe_x - 55, v_y, tbl_z_top)
            vb2 = proj(pipe_x + 55, v_y, tbl_z_top)
            vb3 = proj(pipe_x, v_y, pipe_z_center - pipe_r + 8)
            self.canvas.create_polygon(vb1[0], vb1[1], vb2[0], vb2[1], vb3[0], vb3[1], fill="#334155", outline="#64748b", width=1)

        p_base_col = metal_data.get('pipe_base', '#334155')
        p_body_col = metal_data.get('pipe_body', '#475569')
        p_high_col = metal_data.get('pipe_highlight', '#64748b')
        p_seam_col = metal_data.get('seam_col', '#ff5500')
        p_bead_col = metal_data.get('bead_col', '#f59e0b')
        p_bead_out = metal_data.get('bead_outline', '#ea580c')

        for ang in range(0, 360, 30):
            rad = math.radians(ang)
            dz = math.sin(rad) * pipe_r; dx = math.cos(rad) * pipe_r
            line_col = p_high_col if 45 <= ang <= 135 else (p_body_col if 135 <= ang <= 270 else p_base_col)
            p_s = proj(pipe_x + dx, pipe_y_start, pipe_z_center + dz)
            p_m1 = proj(pipe_x + dx, -10, pipe_z_center + dz)
            p_m2 = proj(pipe_x + dx, 10, pipe_z_center + dz)
            p_e = proj(pipe_x + dx, pipe_y_end, pipe_z_center + dz)
            self.canvas.create_line(p_s[0], p_s[1], p_m1[0], p_m1[1], fill=line_col, width=3)
            self.canvas.create_line(p_m2[0], p_m2[1], p_e[0], p_e[1], fill=line_col, width=3)

        # Pipe End Flange Caps
        for y_pos in [pipe_y_start, pipe_y_end]:
            ring_pts = [proj(pipe_x + math.cos(math.radians(a))*pipe_r, y_pos, pipe_z_center + math.sin(math.radians(a))*pipe_r) for a in range(0, 360, 18)]
            flat_pts = [c for pt in ring_pts for c in pt]
            self.canvas.create_polygon(flat_pts, fill=p_base_col, outline=p_high_col, width=2)

        # Circular Beveled Weld Seam
        seam_pts = [proj(pipe_x + math.cos(math.radians(a))*pipe_r, 0, pipe_z_center + math.sin(math.radians(a))*pipe_r) for a in range(0, 190, 12)]
        for i in range(len(seam_pts) - 1):
            self.canvas.create_line(seam_pts[i][0], seam_pts[i][1], seam_pts[i+1][0], seam_pts[i+1][1], fill=p_seam_col, width=4)

        # Deposited Weld Beads with Metallurgy Color Matching
        for wb in self.weld_bead_history:
            p_wb = proj(*wb)
            self.canvas.create_oval(p_wb[0]-3, p_wb[1]-3, p_wb[0]+3, p_wb[1]+3, fill=p_bead_col, outline=p_bead_out, width=1)

        # Active Material Badge on Workpiece
        lbl_p = proj(pipe_x, pipe_y_start - 35, pipe_z_center + 45)
        self.canvas.create_text(lbl_p[0], lbl_p[1], text=f"WORKPIECE: {metal_data['code']}", fill="#38bdf8", font=('Segoe UI', 8, 'bold'))

        # ----------------------------------------------------------------------
        # 4. Robot Base Pedestal (Ground mounting plate)
        # ----------------------------------------------------------------------
        base_col = "#e05300" if self.is_powered_on else "#334155"
        ped_bot = proj(0, 0, 0); ped_top = proj(0, 0, 90)
        self.canvas.create_oval(ped_bot[0]-48, ped_bot[1]-18, ped_bot[0]+48, ped_bot[1]+18, fill="#111520", outline="#2b3345", width=2)
        self.canvas.create_line(ped_bot[0]-48, ped_bot[1], ped_top[0]-42, ped_top[1], fill="#2b3345", width=2)
        self.canvas.create_line(ped_bot[0]+48, ped_bot[1], ped_top[0]+42, ped_top[1], fill="#2b3345", width=2)
        self.canvas.create_oval(ped_top[0]-42, ped_top[1]-16, ped_top[0]+42, ped_top[1]+16, fill=base_col, outline="#ff7722" if self.is_powered_on else "#475569", width=2)

        for ba in range(0, 360, 45):
            bx = math.cos(math.radians(ba)) * 38; by = math.sin(math.radians(ba)) * 38
            p_b = proj(bx, by, 5)
            self.canvas.create_oval(p_b[0]-2, p_b[1]-2, p_b[0]+2, p_b[1]+2, fill="#94a3b8", outline="")

        # ----------------------------------------------------------------------
        # 5. Kinematic 6-Axis Robot Arm
        # ----------------------------------------------------------------------
        if joints is None:
            joints, _, _ = self.kinematics.solve(self.disp_pos['X'], self.disp_pos['Y'], self.disp_pos['Z'])

        pj0 = proj(*joints['J0'])
        pj1 = proj(*joints['J1'])
        pj2 = proj(*joints['J2'])
        pj3 = proj(*joints['J3'])
        pj4 = proj(*joints['J4'])
        ptcp = proj(*joints['TCP'])

        # Motion Path Ribbon
        if self.is_powered_on and self.show_trail.get() and len(self.path_history) > 1:
            pts = [proj(*pt) for pt in self.path_history]
            for i in range(len(pts) - 1):
                self.canvas.create_line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], fill="#00f2fe", width=2)

        col_cast = "#ea580c" if self.is_powered_on else "#475569"
        col_accent = "#ff6a13" if self.is_powered_on else "#334155"
        col_dark = "#171d29" if self.is_powered_on else "#0f172a"

        # Link 0-1: Turntable Carousel
        self.canvas.create_line(pj0[0], pj0[1], pj1[0], pj1[1], fill=col_dark, width=22, capstyle='round')
        self.canvas.create_line(pj0[0], pj0[1], pj1[0], pj1[1], fill=col_cast, width=15, capstyle='round')

        # Link 1-2: Shoulder Fork Housing
        self.canvas.create_line(pj1[0], pj1[1], pj2[0], pj2[1], fill=col_dark, width=20, capstyle='round')
        self.canvas.create_line(pj1[0], pj1[1], pj2[0], pj2[1], fill=col_cast, width=14, capstyle='round')

        # Counterbalance Cylinder Strut
        strut_p1 = (pj1[0] - 12, pj1[1] + 12); strut_p2 = (pj2[0] - 10, pj2[1] - 16)
        self.canvas.create_line(strut_p1[0], strut_p1[1], strut_p2[0], strut_p2[1], fill="#0f172a", width=6, capstyle='round')
        self.canvas.create_line(strut_p1[0], strut_p1[1], strut_p2[0], strut_p2[1], fill="#94a3b8", width=2, capstyle='round')

        # Link 2-3: Upper Arm (L1 = 430mm constant)
        self.canvas.create_line(pj2[0], pj2[1], pj3[0], pj3[1], fill=col_dark, width=18, capstyle='round')
        self.canvas.create_line(pj2[0], pj2[1], pj3[0], pj3[1], fill=col_accent, width=12, capstyle='round')

        # Link 3-4: Forearm (L2 = 430mm constant)
        self.canvas.create_line(pj3[0], pj3[1], pj4[0], pj4[1], fill=col_dark, width=15, capstyle='round')
        self.canvas.create_line(pj3[0], pj3[1], pj4[0], pj4[1], fill=col_cast, width=9, capstyle='round')

        # Draped Corrugated Cable Dress-Pack
        self.canvas.create_line(pj1[0]+8, pj1[1]-6, pj2[0]+12, pj2[1]-8, pj3[0]+10, pj3[1]-4, pj4[0]+6, pj4[1]-2,
                                fill="#080c14", width=5, smooth=True)

        # Link 4-TCP: Robotic Curved Welding Torch (L3 = 140mm constant)
        self.canvas.create_line(pj4[0], pj4[1], ptcp[0], ptcp[1], fill="#1e293b", width=8, capstyle='round')
        self.canvas.create_line(pj4[0], pj4[1], ptcp[0], ptcp[1], fill="#94a3b8", width=4, capstyle='round')

        # Gas Shroud Nozzle
        torch_dx = ptcp[0] - pj4[0]; torch_dy = ptcp[1] - pj4[1]
        t_dist = math.sqrt(torch_dx**2 + torch_dy**2) + 1e-6
        nx = torch_dx / t_dist; ny = torch_dy / t_dist
        tip_p = (ptcp[0] + nx * 7, ptcp[1] + ny * 7)
        self.canvas.create_line(ptcp[0], ptcp[1], tip_p[0], tip_p[1], fill="#d97706", width=6, capstyle='round')

        # Joint Hub Caps
        hub_border = "#ff7722" if self.is_powered_on else "#ef4444"
        for p, r in [(pj1, 10), (pj2, 9), (pj3, 8), (pj4, 7)]:
            self.canvas.create_oval(p[0]-r, p[1]-r, p[0]+r, p[1]+r, fill="#0f172a", outline=hub_border, width=2)

        # ----------------------------------------------------------------------
        # 6. Live Welding Arc Flare & Spark Dynamics
        # ----------------------------------------------------------------------
        if self.is_welding:
            arc_glow_col = metal_data.get('arc_glow', '#00e5ff')
            arc_core_col = metal_data.get('arc_core', '#ffffff')

            flash_rad = 7 if self.arc_flash_tick % 2 == 0 else 9
            self.canvas.create_oval(ptcp[0]-flash_rad, ptcp[1]-flash_rad, ptcp[0]+flash_rad, ptcp[1]+flash_rad, fill=arc_glow_col, outline="", width=0)
            self.canvas.create_oval(ptcp[0]-flash_rad//2, ptcp[1]-flash_rad//2, ptcp[0]+flash_rad//2, ptcp[1]+flash_rad//2, fill=arc_core_col, outline="")

            # Live Arc Banner Badge
            self.canvas.create_rectangle(w - 240, 16, w - 16, 52, fill="#052e16", outline="#22c55e", width=2)
            self.canvas.create_text(w - 128, 34, text=f"ARC WELDING: {metal_data['code'][:16]}", fill="#4ade80", font=('Segoe UI', 8, 'bold'))
        else:
            tip_col = "#00ffcc" if self.is_powered_on else "#ef4444"
            self.canvas.create_oval(ptcp[0]-4, ptcp[1]-4, ptcp[0]+4, ptcp[1]+4, fill=tip_col, outline="#ffffff", width=1)

        for p in self.particles:
            pp = proj(p['x'], p['y'], p['z'])
            size = max(1, int(p['life'] * 2))
            self.canvas.create_oval(pp[0]-size, pp[1]-size, pp[0]+size, pp[1]+size, fill=p['color'], outline="")

        # ----------------------------------------------------------------------
        # 7. E-STOP OVERLAY & SAFETY INTERLOCK HUD
        # ----------------------------------------------------------------------
        if not self.is_powered_on:
            flash_on = (self.estop_flash_tick < 8)
            border_col = "#ef4444" if flash_on else "#7f1d1d"
            bg_col = "#450a0a"

            bx1, by1 = w // 2 - 240, 20
            bx2, by2 = w // 2 + 240, 78
            self.canvas.create_rectangle(bx1, by1, bx2, by2, fill=bg_col, outline=border_col, width=3)
            self.canvas.create_text(w // 2, 38, text="EMERGENCY STOP ENGAGED", fill="#fca5a5" if flash_on else "#ffffff", font=('Segoe UI', 11, 'bold'))
            self.canvas.create_text(w // 2, 58, text="IEC 62061 SIL 3 / EN ISO 13849-1 Cat. 4 | 400V Drives Locked Out - Mechanical Brakes Clamped", fill="#f87171", font=('Segoe UI', 8))

        # HUD Coordinates & Gizmo
        status_txt = "ONLINE" if self.is_powered_on else "DRIVES LOCKED"
        status_clr = "#22c55e" if self.is_powered_on else "#ef4444"
        self.canvas.create_text(
            16, 20,
            text=f"TCP: X={self.disp_pos['X']:6.1f}  Y={self.disp_pos['Y']:6.1f}  Z={self.disp_pos['Z']:6.1f} mm  |  {status_txt} [{self.auto_step_name}]",
            fill=status_clr,
            font=('Consolas', 9, 'bold'),
            anchor='w'
        )

        # 3D Triad Gizmo
        gx0, gy0 = 50, h - 50
        g_len = 34
        for axis_name, (ax, ay, az), col in [("X", (1, 0, 0), "#ef4444"), ("Y", (0, 1, 0), "#22c55e"), ("Z", (0, 0, 1), "#38bdf8")]:
            px, py, _ = self._project_point(ax * g_len, ay * g_len, az * g_len, gx0, gy0, 1.0)
            self.canvas.create_line(gx0, gy0, px, py, fill=col, width=3, arrow='last')
            self.canvas.create_text(px + 6, py, text=axis_name, fill=col, font=('Segoe UI', 8, 'bold'))


# ==============================================================================
# 6. APPLICATION ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = KukaVisualControlUI(root)
    root.mainloop()
