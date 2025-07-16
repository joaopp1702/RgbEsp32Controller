import serial
import time
import numpy as np
import colorsys
import threading
import tkinter as tk
from tkinter import ttk, colorchooser
import json
import os

NUM_LEDS = 20
PORT = 'COM8'  # porta fixa conforme seu pedido
BAUD = 115200

# Inicializa conexão serial
ser = serial.Serial(PORT, BAUD, timeout=1)

prefix = b'Ada' + bytes([ (NUM_LEDS * 3) >> 8, (NUM_LEDS * 3) & 0xFF, 0x00 ])

mode = 0
step = 0
speed = 30  # ms delay default
base_color_hsv = (0.0, 1.0, 1.0)  # cor base (vermelho)

lock = threading.Lock()

CONFIG_FILE = 'config.json'

# --- Funções para salvar e carregar configuração ---

def save_config():
    config = {
        'mode': mode,
        'speed': speed,
        'base_color_hsv': base_color_hsv
    }
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
    except Exception as e:
        print(f"Erro ao salvar config: {e}")

def load_config():
    global mode, speed, base_color_hsv
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            mode = config.get('mode', 0)
            speed = config.get('speed', 30)
            base_color_hsv = tuple(config.get('base_color_hsv', (0.0, 1.0, 1.0)))
        except Exception as e:
            print(f"Erro ao carregar config: {e}")

# --- Funções de controle LEDs ---

def send_leds(rgb_list):
    data = bytearray()
    for r, g, b in rgb_list:
        data.extend([g, r, b])  # Adalight usa GRB
    ser.write(prefix + data)

def hsv_to_rgb(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return int(r*255), int(g*255), int(b*255)

# --- Efeitos ---

def rainbow_effect(step, base_color=None):
    leds = []
    for i in range(NUM_LEDS):
        h = (step + i * 256 // NUM_LEDS) % 256
        leds.append(hsv_to_rgb(h / 256.0, 1.0, 1.0))
    return leds

def breathing_effect(step, base_color=None):
    brightness = (np.sin(step / 10.0) + 1) / 2
    if base_color:
        h, s, v = base_color
        color = hsv_to_rgb(h, s, brightness)
    else:
        color = (int(255 * brightness), 0, int(255 * (1 - brightness)))
    return [color] * NUM_LEDS

def random_color(step, base_color=None):
    return [(np.random.randint(255), np.random.randint(255), np.random.randint(255)) for _ in range(NUM_LEDS)]

def color_wave(step, base_color=None):
    leds = []
    for i in range(NUM_LEDS):
        h = ((step + i*10) % 360) / 360.0
        leds.append(hsv_to_rgb(h, 1.0, 0.8))
    return leds

def sparkle(step, base_color=None):
    leds = []
    for i in range(NUM_LEDS):
        if np.random.rand() < 0.1:
            leds.append((255, 255, 255))
        else:
            leds.append((0, 0, 50))
    return leds

def theater_chase(step, base_color=None):
    leds = []
    c = (255, 0, 0) if not base_color else hsv_to_rgb(*base_color)
    for i in range(NUM_LEDS):
        if (i + step//5) % 3 == 0:
            leds.append(c)
        else:
            leds.append((0, 0, 0))
    return leds

def color_chase(step, base_color=None):
    leds = []
    base_hue = (step % 360) / 360.0
    for i in range(NUM_LEDS):
        h = (base_hue + i/NUM_LEDS) % 1.0
        leds.append(hsv_to_rgb(h, 1.0, 0.5))
    return leds

def pulse(step, base_color=None):
    brightness = (np.sin(step / 15.0) + 1) / 2 * 0.8 + 0.2
    if base_color:
        h, s, v = base_color
        color = hsv_to_rgb(h, s, brightness)
    else:
        color = (int(255 * brightness), int(100 * brightness), 0)
    return [color] * NUM_LEDS

def fire(step, base_color=None):
    leds = []
    for i in range(NUM_LEDS):
        flicker = np.random.uniform(0.5, 1.0)
        r = int(255 * flicker)
        g = int(50 * flicker)
        b = 0
        leds.append((r, g, b))
    return leds

def ocean_wave(step, base_color=None):
    leds = []
    for i in range(NUM_LEDS):
        h = (210 + 30*np.sin(step/20 + i/3)) % 360
        leds.append(hsv_to_rgb(h/360, 0.7, 0.6))
    return leds

def strobe(step, base_color=None):
    on = (step // 5) % 2 == 0
    color = (255, 255, 255) if on else (0, 0, 0)
    return [color] * NUM_LEDS

def gradient_rainbow(step, base_color=None):
    leds = []
    for i in range(NUM_LEDS):
        h = ((step + i*10) % 360) / 360.0
        s = 1.0
        v = i / NUM_LEDS
        leds.append(hsv_to_rgb(h, s, v))
    return leds

def twinkle(step, base_color=None):
    leds = []
    for i in range(NUM_LEDS):
        brightness = 0.2 + 0.8 * np.random.rand()
        leds.append((int(255*brightness), int(255*brightness), int(255*brightness)))
    return leds

def blink(step, base_color=None):
    on = (step // 10) % 2 == 0
    c = (255, 255, 255) if not base_color else hsv_to_rgb(*base_color)
    color = c if on else (0, 0, 0)
    return [color] * NUM_LEDS

def color_wipe(step, base_color=None):
    leds = []
    pos = step % NUM_LEDS
    c = (255, 0, 0) if not base_color else hsv_to_rgb(*base_color)
    for i in range(NUM_LEDS):
        if i <= pos:
            leds.append(c)
        else:
            leds.append((0, 0, 0))
    return leds

def scanner(step, base_color=None):
    leds = []
    pos = step % (2 * NUM_LEDS - 2)
    if pos >= NUM_LEDS:
        pos = 2 * NUM_LEDS - 2 - pos
    c = (255, 0, 0) if not base_color else hsv_to_rgb(*base_color)
    for i in range(NUM_LEDS):
        if i == pos:
            leds.append(c)
        else:
            leds.append((0, 0, 0))
    return leds

def running_lights(step, base_color=None):
    leds = []
    for i in range(NUM_LEDS):
        brightness = (np.sin((step / 5.0) + (i * np.pi / NUM_LEDS)) + 1) / 2
        if base_color:
            h, s, v = base_color
            val = brightness * v
            leds.append(hsv_to_rgb(h, s, val))
        else:
            leds.append((int(255 * brightness), 0, int(255 * (1 - brightness))))
    return leds

def fade(step, base_color=None):
    leds = []
    h = (step % 360) / 360.0
    s, v = 1.0, 0.5
    if base_color:
        _, s, v = base_color
    for _ in range(NUM_LEDS):
        leds.append(hsv_to_rgb(h, s, v))
    return leds

def confetti(step, base_color=None):
    leds = []
    for i in range(NUM_LEDS):
        base = (np.random.rand() < 0.1)
        c = hsv_to_rgb(*base_color) if base_color else (255, 255, 255)
        leds.append(c if base else (0,0,0))
    return leds

def sinelon(step, base_color=None):
    leds = []
    pos = step % NUM_LEDS
    c = hsv_to_rgb(*base_color) if base_color else (255, 0, 0)
    for i in range(NUM_LEDS):
        if i == pos:
            leds.append(c)
        else:
            leds.append((0, 0, 0))
    return leds

def bpm(step, base_color=None):
    leds = []
    beats_per_minute = 120
    beat = (step * beats_per_minute / 60) % 1
    val = abs(np.sin(beat * 2 * np.pi))
    for _ in range(NUM_LEDS):
        if base_color:
            h, s, _ = base_color
            leds.append(hsv_to_rgb(h, s, val))
        else:
            leds.append((int(255 * val), 0, 0))
    return leds

def juggle(step, base_color=None):
    leds = []
    for i in range(NUM_LEDS):
        pos = (step + i * 10) % NUM_LEDS
        brightness = (np.sin((step / 3.0) + i) + 1) / 2
        if base_color:
            h, s, v = base_color
            leds.append(hsv_to_rgb(h, s, brightness * v))
        else:
            leds.append((int(255 * brightness), 0, 0))
    return leds

effects = [
    rainbow_effect,
    breathing_effect,
    random_color,
    color_wave,
    sparkle,
    theater_chase,
    color_chase,
    pulse,
    fire,
    ocean_wave,
    strobe,
    gradient_rainbow,
    twinkle,
    blink,
    color_wipe,
    scanner,
    running_lights,
    fade,
    confetti,
    sinelon,
    bpm,
    juggle,
]

# Quais efeitos aceitam cor customizada
effects_accept_color = [
    True, True, False, False, False, True, False, True, False, False,
    False, False, False, True, True, True, True, True, True, True,
    True, True
]

# --- Funções da GUI ---

def effect_loop():
    global step
    while True:
        with lock:
            current_mode = mode
            current_speed = speed
            base_col = base_color_hsv if effects_accept_color[current_mode] else None
        leds = effects[current_mode](step, base_col)
        send_leds(leds)
        step += 1
        time.sleep(current_speed / 1000)

def on_mode_change(event):
    global mode
    selected = mode_combo.get()
    try:
        idx = int(selected.split(":")[0])
        if 0 <= idx < len(effects):
            with lock:
                mode = idx
            update_color_picker_state()
        else:
            print(f"Índice de efeito inválido: {idx}")
    except Exception as e:
        print(f"Erro ao trocar efeito: {e}")

def on_speed_change(val):
    global speed
    with lock:
        speed = int(float(val))

def update_color_picker_state():
    if effects_accept_color[mode]:
        color_btn.config(state="normal")
    else:
        color_btn.config(state="disabled")

def choose_color():
    global base_color_hsv
    color_code = colorchooser.askcolor(title="Escolha cor base")
    if color_code and color_code[0]:
        r, g, b = [x/255 for x in color_code[0]]
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        with lock:
            base_color_hsv = (h, s, v)
        update_color_display()
        print(f"Cor base definida HSV: {base_color_hsv}")

def update_color_display():
    # Atualiza a cor do botão para mostrar a cor selecionada
    r, g, b = [int(c * 255) for c in base_color_hsv_to_rgb(base_color_hsv)]
    hex_color = f"#{r:02x}{g:02x}{b:02x}"
    color_btn.config(style="Color.TButton")
    style.configure("Color.TButton", background=hex_color, foreground=hex_color)

def base_color_hsv_to_rgb(hsv):
    h, s, v = hsv
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return int(r*255), int(g*255), int(b*255)

# --- Setup GUI ---

root = tk.Tk()
root.title("Mini RGB Controller")

style = ttk.Style()
style.theme_use('clam')  # tema mais moderno para ttk

mode_var = tk.IntVar(value=mode)

ttk.Label(root, text="Selecione o efeito:").pack(padx=10, pady=5)

mode_combo = ttk.Combobox(
    root,
    values=[f"{i}: {effects[i].__name__}" for i in range(len(effects))],
    state="readonly"
)
mode_combo.current(mode)
mode_combo.pack(padx=10, pady=5)
mode_combo.bind("<<ComboboxSelected>>", on_mode_change)

ttk.Label(root, text="Velocidade (ms delay):").pack(padx=10, pady=5)
speed_scale = ttk.Scale(root, from_=10, to=200, orient=tk.HORIZONTAL, command=on_speed_change)
speed_scale.set(speed)
speed_scale.pack(padx=10, pady=5)

color_btn = ttk.Button(root, text="Escolher cor base", command=choose_color)
color_btn.pack(padx=10, pady=10)

update_color_picker_state()
update_color_display()

def on_close():
    save_config()
    with lock:
        global connected
        connected = False
    if ser and ser.is_open:
        ser.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

thread = threading.Thread(target=effect_loop, daemon=True)
thread.start()

root.mainloop()
