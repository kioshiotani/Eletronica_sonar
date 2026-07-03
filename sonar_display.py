#!/usr/bin/env python3
"""
Interface gráfica (radar) para o sonar com Arduino + HC-SR04 + Servo

Requisitos:
    pip3 install pygame pyserial

Uso:
    python3 sonar_gui_pygame.py                  -> detecta a porta automaticamente
    python3 sonar_gui_pygame.py /dev/ttyACM0      -> especifica a porta manualmente
"""

import sys
import math
import time
import queue
import threading

import pygame

try:
    import serial
    from serial.tools import list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

# ------------------------- CONFIGURAÇÕES ------------------------- #
BAUD_RATE = 9600
MIN_ANGLE = 30
MAX_ANGLE = 150
MAX_DIST_CM = 40          # distancia maxima mostrada no radar
RING_STEP_CM = 10         # espacamento entre os circulos de referencia
POINT_LIFETIME = 3.0      # segundos que um eco fica visivel
FPS = 60

WIDTH, HEIGHT = 900, 600
MARGIN_BOTTOM = 60

BG_COLOR = (0, 0, 0)
GRID_COLOR = (10, 90, 10)
GRID_TEXT_COLOR = (30, 140, 30)
SWEEP_COLOR = (50, 255, 50)
TRAIL_COLOR = (15, 60, 15)
TEXT_COLOR = (50, 255, 50)
ECHO_COLOR_NEW = (255, 40, 40)
ECHO_COLOR_OLD = (25, 20, 20)
# ------------------------------------------------------------------ #


def find_serial_port():
    if not SERIAL_AVAILABLE:
        return None
    for p in list_ports.comports():
        desc = (p.description or "").lower()
        if "arduino" in desc or "ttyusb" in p.device.lower() or "ttyacm" in p.device.lower():
            return p.device
    return None


class SerialReader(threading.Thread):
    """Lê a porta serial numa thread separada e coloca pares (angulo, distancia) numa fila."""

    def __init__(self, port, baud, out_queue):
        super().__init__(daemon=True)
        self.port = port
        self.baud = baud
        self.out_queue = out_queue
        self._stop = threading.Event()
        self.ser = None
        self.connected = False
        self.error = None

    def run(self):
        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=1)
            time.sleep(2)  # tempo para o Arduino resetar após abrir a serial
            self.connected = True
        except Exception as e:
            self.error = str(e)
            return

        buffer = ""
        while not self._stop.is_set():
            try:
                chunk = self.ser.read(self.ser.in_waiting or 1).decode(errors="ignore")
            except Exception as e:
                self.error = str(e)
                break
            if not chunk:
                continue
            buffer += chunk
            while "." in buffer:
                token, buffer = buffer.split(".", 1)
                token = token.strip()
                if "," in token:
                    ang_s, dist_s = token.split(",", 1)
                    try:
                        self.out_queue.put((int(ang_s), int(dist_s)))
                    except ValueError:
                        pass

    def stop(self):
        self._stop.set()
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
            except Exception:
                pass

def polar_to_xy(cx, cy, radius, angle_deg, dist_cm):
    r = (dist_cm / MAX_DIST_CM) * radius
    rad = math.radians(angle_deg)
    x = cx + r * math.cos(rad)
    y = cy - r * math.sin(rad)
    return x, y


def fade_color(alpha, new_color, old_color):
    return tuple(int(o + (n - o) * alpha) for n, o in zip(new_color, old_color))


def draw_arc_lines(surface, cx, cy, radius, color, n_segments=100):
    points = []
    for i in range(n_segments + 1):
        ang = 180 * i / n_segments
        x, y = polar_to_xy(cx, cy, radius, ang, MAX_DIST_CM)
        points.append((x, y))
    pygame.draw.lines(surface, color, False, points, 1)


def main():
    port = None
    simulate = False
    args = sys.argv[1:]
    if args:
        port = args[0]

    if not SERIAL_AVAILABLE and not simulate:
        print("Aviso: pyserial não está instalado. Rodando em modo simulação.")
        print("Instale com: pip3 install pyserial")
        simulate = True

    data_queue = queue.Queue()

    if simulate:
        reader = SimulatedReader(data_queue)
    else:
        chosen_port = port or find_serial_port()
        if chosen_port is None:
            print("Nenhuma porta serial encontrada, iniciando em modo simulação.")
            reader = SimulatedReader(data_queue)
        else:
            reader = SerialReader(chosen_port, BAUD_RATE, data_queue)
    reader.start()

    pygame.init()
    pygame.display.set_caption("Sonar Radar - Arduino")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 16)
    font_small = pygame.font.SysFont("consolas", 12)

    cx, cy = WIDTH // 2, HEIGHT - MARGIN_BOTTOM
    radius = min(cx, cy) - 40

    current_angle = MIN_ANGLE
    current_dist = 0
    points = []  # dicts: angle, dist, ts
    sweep_direction = 1  # 1 = ângulo aumentando (direita->esquerda), -1 = diminuindo (esquerda->direita)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # --- consome dados da serial ---
        while not data_queue.empty():
            angle, dist = data_queue.get()
            if angle != current_angle:
                sweep_direction = 1 if angle > current_angle else -1
            current_angle, current_dist = angle, dist
            if 0 < dist <= MAX_DIST_CM:
                points.append({"angle": angle, "dist": dist, "ts": time.time()})

        now = time.time()
        points = [p for p in points if now - p["ts"] < POINT_LIFETIME]

        # ------------------------- DESENHO ------------------------- #
        screen.fill(BG_COLOR)

        # anéis de distância
        rings = int(MAX_DIST_CM / RING_STEP_CM)
        for i in range(1, rings + 1):
            r = radius * i / rings
            draw_arc_lines(screen, cx, cy, r * MAX_DIST_CM / MAX_DIST_CM, GRID_COLOR)
            label_dist = int(RING_STEP_CM * i)
            lx, ly = polar_to_xy(cx, cy, radius, 5, label_dist)
            txt = font_small.render(f"{label_dist}cm", True, GRID_TEXT_COLOR)
            screen.blit(txt, (lx, ly - 8))

        # linhas de ângulo a cada 30°
        for ang in range(0, 181, 30):
            x, y = polar_to_xy(cx, cy, radius, ang, MAX_DIST_CM)
            pygame.draw.line(screen, GRID_COLOR, (cx, cy), (x, y), 1)
            lx, ly = polar_to_xy(cx, cy, radius * 1.06, ang, MAX_DIST_CM)
            txt = font_small.render(f"{ang}°", True, GRID_TEXT_COLOR)
            screen.blit(txt, (lx - 10, ly - 6))

        # base
        pygame.draw.line(screen, GRID_COLOR, (cx - radius, cy), (cx + radius, cy), 1)

        # rastro do feixe (leque atrás do sweep)
        sweep_x, sweep_y = polar_to_xy(cx, cy, radius, current_angle, MAX_DIST_CM)
        trail_x, trail_y = polar_to_xy(cx, cy, radius, current_angle - 10 * sweep_direction, MAX_DIST_CM)
        pygame.draw.polygon(screen, TRAIL_COLOR, [(cx, cy), (sweep_x, sweep_y), (trail_x, trail_y)])

        # linha do feixe
        pygame.draw.line(screen, SWEEP_COLOR, (cx, cy), (sweep_x, sweep_y), 2)

        # pontos detectados, com fade
        for p in points:
            alpha = max(0.0, 1 - (now - p["ts"]) / POINT_LIFETIME)
            color = fade_color(alpha, ECHO_COLOR_NEW, ECHO_COLOR_OLD)
            x, y = polar_to_xy(cx, cy, radius, p["angle"], p["dist"])
            pygame.draw.circle(screen, color, (int(x), int(y)), 4)

        # origem do sensor
        pygame.draw.circle(screen, SWEEP_COLOR, (cx, cy), 4)

        # HUD: status e leitura atual
        if getattr(reader, "error", None):
            status = f"Erro na serial: {reader.error}"
        elif getattr(reader, "connected", False):
            status = f"Conectado: {getattr(reader, 'port', '?')}"
        else:
            status = "Conectando..."
        screen.blit(font.render(status, True, TEXT_COLOR), (10, 8))

        readout = f"Ângulo: {current_angle:3d}°   Distância: {current_dist:3d} cm"
        readout_surf = font.render(readout, True, TEXT_COLOR)
        screen.blit(readout_surf, (WIDTH - readout_surf.get_width() - 10, 8))

        pygame.display.flip()
        clock.tick(FPS)

    reader.stop()
    pygame.quit()


if __name__ == "__main__":
    main()
