import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import rawpy
import os
import numpy as np
from pillow_heif import register_heif_opener
import io

# ─────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Salva Raw PRO · Cinematic Edition",
    layout="wide",
    initial_sidebar_state="expanded",
)
register_heif_opener()

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;800&family=DM+Mono:wght@300;400&display=swap');
  :root {
    --bg: #0e0e0f; --surface: #181819; --border: #2a2a2d;
    --accent: #e8d5a3; --accent2: #c49a6c; --text: #e8e6e1; --muted: #6b6965;
  }
  html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important; color: var(--text) !important;
    font-family: 'DM Mono', monospace !important;
  }
  [data-testid="stSidebar"] {
    background: var(--surface) !important; border-right: 1px solid var(--border) !important;
  }
  [data-testid="stSidebar"] * { font-family: 'DM Mono', monospace !important; }
  h1 {
    font-family: 'Syne', sans-serif !important; font-weight: 800 !important;
    font-size: clamp(1.6rem, 4vw, 2.6rem) !important; letter-spacing: -0.03em !important;
    color: var(--accent) !important; margin-bottom: 0.2rem !important;
  }
  h3 {
    font-family: 'Syne', sans-serif !important; font-size: 0.75rem !important;
    letter-spacing: 0.18em !important; text-transform: uppercase !important;
    color: var(--muted) !important; border-bottom: 1px solid var(--border) !important;
    padding-bottom: 6px !important; margin-bottom: 12px !important;
  }
  [data-baseweb="select"] > div {
    background: var(--bg) !important; border: 1px solid var(--border) !important;
    border-radius: 6px !important; color: var(--text) !important;
  }
  .stSlider > div > div > div > div { background: var(--accent) !important; }
  .stSlider [data-testid="stThumbValue"] {
    color: var(--accent) !important; font-family: 'DM Mono', monospace !important; font-size: 0.72rem !important;
  }
  label, .stSelectbox label, .stSlider label {
    font-size: 0.7rem !important; letter-spacing: 0.12em !important;
    text-transform: uppercase !important; color: var(--muted) !important;
  }
  .stDownloadButton > button {
    background: transparent !important; border: 1px solid var(--accent2) !important;
    color: var(--accent) !important; font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important; letter-spacing: 0.1em !important;
    border-radius: 6px !important; padding: 10px 20px !important;
    transition: all 0.2s ease !important; width: 100% !important;
  }
  .stDownloadButton > button:hover { background: var(--accent2) !important; color: var(--bg) !important; }
  [data-testid="stFileUploader"] {
    background: var(--surface) !important; border: 1px dashed var(--border) !important;
    border-radius: 10px !important; padding: 24px !important;
  }
  [data-testid="stFileUploader"] * { color: var(--muted) !important; }
  .stAlert {
    background: var(--surface) !important; border: 1px solid var(--border) !important;
    border-radius: 8px !important; color: var(--muted) !important; font-size: 0.8rem !important;
  }
  hr { border-color: var(--border) !important; }
  .img-label {
    font-size: 0.65rem; letter-spacing: 0.2em; text-transform: uppercase;
    color: var(--muted); margin-bottom: 6px; display: block;
  }
  .profile-badge {
    display: inline-block; background: var(--accent2); color: var(--bg);
    font-family: 'DM Mono', monospace; font-size: 0.65rem; letter-spacing: 0.12em;
    text-transform: uppercase; padding: 3px 10px; border-radius: 20px; margin-bottom: 14px;
  }
  .bars-badge {
    display: inline-block; background: #111; color: #e8d5a3; border: 1px solid #3a3a3a;
    font-family: 'DM Mono', monospace; font-size: 0.62rem; letter-spacing: 0.15em;
    text-transform: uppercase; padding: 3px 10px; border-radius: 20px;
    margin-bottom: 14px; margin-left: 8px;
  }
  [data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 0.6rem !important; }
  input[type="number"] {
    background: var(--bg) !important; border: 1px solid var(--border) !important;
    color: var(--text) !important; border-radius: 6px !important; font-family: 'DM Mono', monospace !important;
  }
  @media (max-width: 768px) {
    .block-container { padding: 1rem !important; }
    [data-testid="column"] { min-width: 100% !important; }
  }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PERFILES CINEMATOGRÁFICOS
# c=contraste  s=saturacion  b=brillo  rgb=(R,G,B)
# ─────────────────────────────────────────────
PROFILES = {
    # ── CLASICOS & CINE ──
    "Blockbuster · Teal & Orange": {"c": 1.20, "s": 1.30, "b": 1.00, "rgb": (1.10, 1.00, 0.88)},
    "Noir Classic":                {"c": 1.65, "s": 0.00, "b": 0.92, "rgb": (1.00, 1.00, 1.00)},
    "Vintage 70s":                 {"c": 0.90, "s": 0.80, "b": 1.05, "rgb": (1.20, 1.10, 0.78)},
    "Technicolor":                 {"c": 1.40, "s": 1.70, "b": 1.00, "rgb": (1.05, 1.00, 0.95)},
    "Wes Anderson":                {"c": 0.90, "s": 1.20, "b": 1.10, "rgb": (1.20, 0.92, 1.02)},
    "Moonlight":                   {"c": 1.10, "s": 0.90, "b": 0.95, "rgb": (0.80, 0.88, 1.30)},
    "Western Dust":                {"c": 1.20, "s": 0.70, "b": 1.00, "rgb": (1.20, 1.10, 0.78)},
    "Kubrick Cold":                {"c": 1.35, "s": 0.85, "b": 0.90, "rgb": (0.88, 0.95, 1.25)},
    "Godfather Warm":              {"c": 1.30, "s": 0.75, "b": 0.88, "rgb": (1.18, 1.05, 0.80)},
    "Apocalypse Now":              {"c": 1.15, "s": 0.90, "b": 0.95, "rgb": (1.10, 1.05, 0.82)},
    "Blade Runner 2049":           {"c": 1.25, "s": 1.10, "b": 0.90, "rgb": (1.05, 0.95, 1.20)},
    "Mad Max Fury Road":           {"c": 1.40, "s": 1.20, "b": 1.05, "rgb": (1.18, 1.08, 0.72)},
    "Lawrence of Arabia":          {"c": 1.20, "s": 0.95, "b": 1.10, "rgb": (1.22, 1.12, 0.80)},
    "Casablanca (Tinted)":         {"c": 1.50, "s": 0.15, "b": 0.95, "rgb": (1.05, 1.02, 0.92)},
    "La La Land":                  {"c": 0.95, "s": 1.40, "b": 1.08, "rgb": (1.12, 0.98, 1.10)},
    # ── FILM STOCKS ──
    "Kodak Portra 400":            {"c": 1.10, "s": 1.10, "b": 1.05, "rgb": (1.10, 1.05, 0.95)},
    "Kodak Ektar 100":             {"c": 1.30, "s": 1.55, "b": 1.00, "rgb": (1.10, 1.00, 0.90)},
    "Kodak Gold 200":              {"c": 1.05, "s": 1.20, "b": 1.08, "rgb": (1.15, 1.08, 0.85)},
    "Kodak Tri-X 400 (BW)":        {"c": 1.70, "s": 0.00, "b": 0.90, "rgb": (1.00, 1.00, 1.00)},
    "Kodak Vision3 500T":          {"c": 1.15, "s": 1.05, "b": 0.92, "rgb": (0.92, 0.98, 1.18)},
    "Fuji Velvia 50":              {"c": 1.35, "s": 1.65, "b": 1.00, "rgb": (0.90, 1.10, 1.02)},
    "Fuji Provia 100F":            {"c": 1.20, "s": 1.30, "b": 1.02, "rgb": (0.95, 1.05, 1.08)},
    "Fuji Pro 400H":               {"c": 1.00, "s": 1.00, "b": 1.10, "rgb": (1.05, 1.08, 1.05)},
    "Fuji Neopan Acros (BW)":      {"c": 1.80, "s": 0.00, "b": 0.88, "rgb": (1.00, 1.00, 1.00)},
    "Agfa Vista 200":              {"c": 1.20, "s": 1.20, "b": 1.00, "rgb": (1.00, 1.00, 1.12)},
    "Ilford HP5 (BW)":             {"c": 1.55, "s": 0.00, "b": 0.95, "rgb": (1.00, 1.00, 1.00)},
    "Polaroid 600":                {"c": 0.88, "s": 0.80, "b": 1.08, "rgb": (1.12, 1.08, 1.00)},
    "Polaroid SX-70":              {"c": 0.85, "s": 1.10, "b": 1.12, "rgb": (1.08, 1.05, 0.98)},
    "Lomography 800":              {"c": 1.10, "s": 1.40, "b": 0.95, "rgb": (1.18, 0.95, 1.10)},
    "Cinestill 800T":              {"c": 1.20, "s": 1.15, "b": 0.90, "rgb": (1.08, 0.92, 1.22)},
    "Faded Film":                  {"c": 0.80, "s": 0.60, "b": 1.10, "rgb": (1.02, 1.00, 0.98)},
    "Bleach Bypass":               {"c": 1.70, "s": 0.40, "b": 0.88, "rgb": (1.00, 1.00, 1.00)},
    # ── MODERNOS & EDITORIALES ──
    "Moody Dark":                  {"c": 1.50, "s": 0.70, "b": 0.85, "rgb": (0.80, 0.80, 0.82)},
    "High Key Bright":             {"c": 0.80, "s": 1.10, "b": 1.15, "rgb": (1.08, 1.08, 1.10)},
    "Muted Tones":                 {"c": 1.00, "s": 0.40, "b": 1.00, "rgb": (1.00, 1.00, 1.00)},
    "Warm Sunset":                 {"c": 1.10, "s": 1.40, "b": 1.05, "rgb": (1.28, 1.00, 0.78)},
    "Cold Winter":                 {"c": 1.00, "s": 0.80, "b": 1.00, "rgb": (0.90, 1.00, 1.22)},
    "Golden Hour":                 {"c": 1.10, "s": 1.50, "b": 1.05, "rgb": (1.22, 1.10, 0.68)},
    "Sepia Nostalgia":             {"c": 1.10, "s": 0.50, "b": 1.00, "rgb": (1.22, 1.02, 0.70)},
    "Urban Green":                 {"c": 1.20, "s": 1.10, "b": 0.95, "rgb": (0.88, 1.22, 1.00)},
    "Deep Ocean":                  {"c": 1.20, "s": 1.20, "b": 0.90, "rgb": (0.72, 0.98, 1.20)},
    "High Contrast":               {"c": 2.00, "s": 1.20, "b": 1.00, "rgb": (1.00, 1.00, 1.00)},
    "Shadow Crush":                {"c": 1.60, "s": 0.90, "b": 0.85, "rgb": (0.90, 0.90, 0.92)},
    "Soft Glow":                   {"c": 0.90, "s": 1.10, "b": 1.10, "rgb": (1.02, 1.02, 1.04)},
    "Silky Smooth":                {"c": 0.90, "s": 0.90, "b": 1.05, "rgb": (1.04, 1.04, 1.06)},
    "Pastel Dream":                {"c": 0.80, "s": 0.90, "b": 1.10, "rgb": (1.12, 1.10, 1.20)},
    "Vibrant Nature":              {"c": 1.20, "s": 1.80, "b": 1.00, "rgb": (1.00, 1.10, 1.00)},
    "Royal Gold":                  {"c": 1.20, "s": 1.20, "b": 1.00, "rgb": (1.30, 1.18, 0.78)},
    "Olive Grove":                 {"c": 1.00, "s": 1.10, "b": 1.00, "rgb": (1.10, 1.22, 0.90)},
    "Retro Digital":               {"c": 1.10, "s": 1.30, "b": 1.00, "rgb": (1.00, 1.20, 1.10)},
    # ── SCI-FI & PELICULAS ──
    "Cyberpunk":                   {"c": 1.30, "s": 1.50, "b": 0.90, "rgb": (1.15, 0.78, 1.30)},
    "Matrix":                      {"c": 1.20, "s": 1.10, "b": 0.90, "rgb": (0.75, 1.32, 0.78)},
    "Night Vision":                {"c": 1.30, "s": 1.00, "b": 0.85, "rgb": (0.50, 1.52, 0.50)},
    "Neon Night":                  {"c": 1.40, "s": 1.70, "b": 0.85, "rgb": (1.12, 0.68, 1.42)},
    "Infrared":                    {"c": 1.50, "s": 0.60, "b": 1.10, "rgb": (1.30, 0.75, 0.65)},
    "Tron Legacy":                 {"c": 1.40, "s": 1.20, "b": 0.82, "rgb": (0.75, 1.00, 1.40)},
    "Interstellar":                {"c": 1.20, "s": 0.85, "b": 0.95, "rgb": (0.95, 1.00, 1.12)},
    "Dune":                        {"c": 1.15, "s": 0.90, "b": 1.05, "rgb": (1.18, 1.10, 0.75)},
    "The Revenant":                {"c": 1.25, "s": 0.80, "b": 0.92, "rgb": (0.92, 1.00, 1.10)},
    "Drive":                       {"c": 1.20, "s": 1.10, "b": 0.90, "rgb": (1.05, 0.85, 1.15)},
    "Crimson Peak":                {"c": 1.30, "s": 1.20, "b": 0.88, "rgb": (1.20, 0.82, 0.82)},
    "Her (Spike Jonze)":           {"c": 0.95, "s": 1.30, "b": 1.05, "rgb": (1.18, 0.95, 0.88)},
    "Joker 2019":                  {"c": 1.40, "s": 1.10, "b": 0.85, "rgb": (1.10, 1.00, 0.75)},
    "Mad Max B&W":                 {"c": 1.80, "s": 0.00, "b": 1.00, "rgb": (1.00, 1.00, 1.00)},
    # ── CREATIVOS ──
    "Forest Tale":                 {"c": 1.10, "s": 1.20, "b": 1.00, "rgb": (0.90, 1.30, 0.90)},
    "Crimson":                     {"c": 1.20, "s": 1.10, "b": 0.95, "rgb": (1.40, 0.80, 0.80)},
    "Cinema Blue":                 {"c": 1.10, "s": 1.10, "b": 0.95, "rgb": (0.88, 0.98, 1.30)},
    "B&W Dramatic":                {"c": 1.90, "s": 0.00, "b": 0.90, "rgb": (1.00, 1.00, 1.00)},
    "Lomography Cross":            {"c": 1.20, "s": 1.60, "b": 0.95, "rgb": (1.20, 0.88, 1.15)},
    "Duotone Sunset":              {"c": 1.15, "s": 0.30, "b": 1.00, "rgb": (1.35, 0.90, 0.60)},
    "Duotone Midnight":            {"c": 1.20, "s": 0.25, "b": 0.88, "rgb": (0.65, 0.80, 1.40)},
    "Mercury":                     {"c": 1.30, "s": 0.20, "b": 0.95, "rgb": (0.92, 1.00, 1.08)},
}

PROFILE_GROUPS = {
    "— Sin Perfil —": ["— Sin Perfil —"],
    "🎬 Clasicos & Cine": [
        "Blockbuster · Teal & Orange", "Noir Classic", "Vintage 70s", "Technicolor",
        "Wes Anderson", "Moonlight", "Western Dust", "Kubrick Cold", "Godfather Warm",
        "Apocalypse Now", "Blade Runner 2049", "Mad Max Fury Road", "Lawrence of Arabia",
        "Casablanca (Tinted)", "La La Land",
    ],
    "🎞 Film Stocks · Analogico": [
        "Kodak Portra 400", "Kodak Ektar 100", "Kodak Gold 200", "Kodak Tri-X 400 (BW)",
        "Kodak Vision3 500T", "Fuji Velvia 50", "Fuji Provia 100F", "Fuji Pro 400H",
        "Fuji Neopan Acros (BW)", "Agfa Vista 200", "Ilford HP5 (BW)", "Polaroid 600",
        "Polaroid SX-70", "Lomography 800", "Cinestill 800T", "Faded Film", "Bleach Bypass",
    ],
    "🌆 Modernos & Editoriales": [
        "Moody Dark", "High Key Bright", "Muted Tones", "Warm Sunset", "Cold Winter",
        "Golden Hour", "Sepia Nostalgia", "Urban Green", "Deep Ocean", "High Contrast",
        "Shadow Crush", "Soft Glow", "Silky Smooth", "Pastel Dream", "Vibrant Nature",
        "Royal Gold", "Olive Grove", "Retro Digital",
    ],
    "🚀 Sci-Fi & Peliculas": [
        "Cyberpunk", "Matrix", "Night Vision", "Neon Night", "Infrared",
        "Tron Legacy", "Interstellar", "Dune", "The Revenant", "Drive",
        "Crimson Peak", "Her (Spike Jonze)", "Joker 2019", "Mad Max B&W",
    ],
    "✦ Creativos & Duotono": [
        "Forest Tale", "Crimson", "Cinema Blue", "B&W Dramatic",
        "Lomography Cross", "Duotone Sunset", "Duotone Midnight", "Mercury",
    ],
}


# ─────────────────────────────────────────────
# FUNCIONES
# ─────────────────────────────────────────────

def load_image(file_bytes, file_name):
    ext = os.path.splitext(file_name)[1].lower()
    if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.heic', '.heif']:
        return Image.open(file_bytes).convert("RGB")
    elif ext in ['.dng', '.cr2', '.nef', '.arw']:
        with rawpy.imread(file_bytes) as raw:
            rgb = raw.postprocess()
        return Image.fromarray(rgb)
    return None


def apply_cinema_profile(image, profile_name):
    if profile_name == "— Sin Perfil —":
        return image
    img = image.convert("RGB")
    p = PROFILES.get(profile_name)
    if not p:
        return image
    img = ImageEnhance.Contrast(img).enhance(p["c"])
    img = ImageEnhance.Color(img).enhance(p["s"])
    img = ImageEnhance.Brightness(img).enhance(p["b"])
    r, g, b = img.split()
    r = r.point(lambda i: min(255, int(i * p["rgb"][0])))
    g = g.point(lambda i: min(255, int(i * p["rgb"][1])))
    b = b.point(lambda i: min(255, int(i * p["rgb"][2])))
    return Image.merge("RGB", (r, g, b))


def apply_gamma(image, gamma):
    if gamma == 1.0:
        return image
    arr = np.array(image).astype(np.float32)
    arr = np.clip((arr / 255.0) ** (1.0 / gamma) * 255, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def apply_focus(image, amount):
    if amount <= 0:
        return image
    return image.filter(ImageFilter.UnsharpMask(radius=2, percent=int(amount * 100), threshold=3))


def apply_grain(image, intensity):
    """Grano fotografico analogico gaussiano de luminancia."""
    if intensity <= 0:
        return image
    arr = np.array(image).astype(np.float32)
    sigma = intensity * 28.0
    noise = np.random.normal(0, sigma, arr.shape[:2])
    noise_rgb = np.stack([noise] * 3, axis=-1)
    noise_img = Image.fromarray(np.clip(noise_rgb + 128, 0, 255).astype(np.uint8))
    noise_img = noise_img.filter(ImageFilter.GaussianBlur(radius=0.5))
    noise_smooth = np.array(noise_img).astype(np.float32) - 128
    final_noise = noise_rgb * 0.6 + noise_smooth * 0.4
    arr = np.clip(arr + final_noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def apply_glow(image, intensity):
    """Halation/Bloom cinematografico con tinte ambar en altos luces."""
    if intensity <= 0:
        return image
    arr = np.array(image.convert("RGB")).astype(np.float32)
    threshold = 200 - int(intensity * 60)
    highlights = np.clip(arr - threshold, 0, 255)
    radius = 6 + intensity * 12
    hl_blur = Image.fromarray(highlights.astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(radius=radius)
    )
    hl_arr = np.array(hl_blur).astype(np.float32)
    hl_arr[:, :, 0] = np.clip(hl_arr[:, :, 0] * 1.15, 0, 255)
    hl_arr[:, :, 1] = np.clip(hl_arr[:, :, 1] * 1.05, 0, 255)
    hl_arr[:, :, 2] = np.clip(hl_arr[:, :, 2] * 0.85, 0, 255)
    result = np.clip(arr + hl_arr * (intensity * 0.7), 0, 255).astype(np.uint8)
    return Image.fromarray(result)


def apply_vignette(image, strength):
    """Vineta eliptica suave."""
    if strength <= 0:
        return image
    arr = np.array(image).astype(np.float32)
    h, w = arr.shape[:2]
    Y, X = np.ogrid[:h, :w]
    cx, cy = w / 2, h / 2
    mask = 1 - np.sqrt(((X - cx) / cx) ** 2 + ((Y - cy) / cy) ** 2)
    mask = np.clip(mask, 0, 1) ** (1.5 - strength * 1.2)
    mask = np.clip(mask, 0, 1)
    arr = np.clip(arr * np.stack([mask] * 3, axis=-1), 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def apply_letterbox(image, ratio_label):
    """
    Barras cinematograficas (letterbox).
    Agrega barras negras para encuadrar la imagen
    en la relacion de aspecto seleccionada sin recortar.
    """
    RATIOS = {
        "2.39:1  Scope (Panavision)":      2.39,
        "2.35:1  CinemaScope clasico":     2.35,
        "2.20:1  Todd-AO / 70mm":          2.20,
        "1.85:1  Flat americano":          1.85,
        "1.78:1  16:9 widescreen":         16 / 9,
        "1.66:1  European widescreen":     1.66,
        "1.43:1  IMAX nativo":             1.43,
        "2.76:1  Ultra Panavision 70":     2.76,
        "4:3     TV clasica / Academia":   4 / 3,
    }
    target = RATIOS.get(ratio_label)
    if not target:
        return image

    w, h = image.size
    current = w / h

    if abs(current - target) < 0.01:
        return image

    if current < target:
        # imagen mas alta → barras arriba y abajo
        new_h = int(round(w / target))
        canvas = Image.new("RGB", (w, new_h), (0, 0, 0))
        canvas.paste(image, (0, (new_h - h) // 2))
    else:
        # imagen mas ancha → barras izquierda y derecha
        new_w = int(round(h * target))
        canvas = Image.new("RGB", (new_w, h), (0, 0, 0))
        canvas.paste(image, ((new_w - w) // 2, 0))

    return canvas


def process_image(img, profile, gamma, focus, grain, glow, vignette,
                  rotation, resize_pct, letterbox_ratio):
    out = apply_cinema_profile(img, profile)
    if rotation != 0:
        out = out.rotate(-rotation, expand=True)
    out = apply_gamma(out, gamma)
    out = apply_focus(out, focus)
    out = apply_glow(out, glow)
    out = apply_vignette(out, vignette)
    out = apply_grain(out, grain)
    if letterbox_ratio != "— Sin barras —":
        out = apply_letterbox(out, letterbox_ratio)
    if resize_pct < 100:
        w, h = out.size
        out = out.resize(
            (int(w * resize_pct / 100), int(h * resize_pct / 100)),
            Image.Resampling.LANCZOS
        )
    return out


def image_to_bytes(img, quality=95):
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality)
    return buf.getvalue()


# ─────────────────────────────────────────────
# INTERFAZ PRINCIPAL
# ─────────────────────────────────────────────

st.markdown("# SALVA RAW PRO")
st.markdown(
    "<span style='font-size:0.75rem;letter-spacing:0.2em;color:#6b6965;text-transform:uppercase'>"
    "Cinematic Edition v3.0 &nbsp;·&nbsp; 70+ Perfiles &nbsp;·&nbsp; Letterbox Profesional</span>",
    unsafe_allow_html=True
)
st.divider()

# ── SIDEBAR ──
with st.sidebar:
    st.markdown(
        "<span style='font-size:0.65rem;letter-spacing:0.25em;color:#6b6965;text-transform:uppercase'>SALVA RAW PRO</span>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<span style='font-family:Syne,sans-serif;font-size:1.1rem;font-weight:800;color:#e8d5a3'>Cinematic Edition v3</span>",
        unsafe_allow_html=True
    )
    st.markdown(
        "[![PayPal](https://img.shields.io/badge/Donar-PayPal-003087?style=flat&logo=paypal)](https://www.paypal.com/donate/?hosted_button_id=GWJTR9XF6JSY8)"
    )
    st.divider()

    # Perfil
    st.subheader("🎞 Perfil Cinematografico")
    all_perfiles = []
    for items in PROFILE_GROUPS.values():
        all_perfiles.extend(items)
    selected_profile = st.selectbox("Perfil", all_perfiles)
    st.divider()

    # Ajustes base
    st.subheader("⚙️ Ajustes Base")
    gamma   = st.slider("Gamma",   0.1, 3.0, 1.0, 0.05)
    focus   = st.slider("Enfoque", 0.0, 10.0, 0.0, 0.1)
    st.divider()

    # Efectos creativos
    st.subheader("✨ Efectos Creativos")
    grain    = st.slider("Grano Fotografico", 0.0, 1.0, 0.0, 0.01,
                         help="Grano analogico gaussiano de luminancia")
    glow     = st.slider("Glow / Halation",   0.0, 1.0, 0.0, 0.01,
                         help="Bloom cinematografico calido en altos luces")
    vignette = st.slider("Vineta",            0.0, 1.0, 0.0, 0.01,
                         help="Oscurece los bordes para encuadre cinematografico")
    st.divider()

    # Letterbox
    st.subheader("🎥 Letterbox · Barras de Cine")
    letterbox_options = [
        "— Sin barras —",
        "2.39:1  Scope (Panavision)",
        "2.35:1  CinemaScope clasico",
        "2.20:1  Todd-AO / 70mm",
        "1.85:1  Flat americano",
        "1.78:1  16:9 widescreen",
        "1.66:1  European widescreen",
        "1.43:1  IMAX nativo",
        "2.76:1  Ultra Panavision 70",
        "4:3     TV clasica / Academia",
    ]
    letterbox_ratio = st.selectbox(
        "Relacion de Aspecto", letterbox_options,
        help="Encuadra la imagen en el formato cinematografico seleccionado"
    )
    st.divider()

    # Geometria
    st.subheader("📐 Geometria")
    rotation   = st.select_slider("Rotacion",
                                   options=[-270, -180, -90, 0, 90, 180, 270],
                                   value=0, format_func=lambda x: f"{x}°")
    resize_pct = st.slider("Redimensionar %", 10, 100, 100, 5)
    st.divider()
    st.markdown(
        "<span style='font-size:0.62rem;color:#6b6965'>v3.0 · Salva Rosales · 70+ perfiles</span>",
        unsafe_allow_html=True
    )


# ── ZONA PRINCIPAL ──
uploaded_file = st.file_uploader(
    "Arrastra tu imagen o haz clic para seleccionar",
    type=["jpg", "jpeg", "png", "dng", "cr2", "nef", "arw", "heic", "heif"],
    label_visibility="collapsed"
)

if uploaded_file:
    img_orig = load_image(uploaded_file, uploaded_file.name)

    if img_orig is None:
        st.error("No se pudo cargar la imagen. Formato no soportado.")
    else:
        img_mod = process_image(
            img_orig, selected_profile, gamma, focus,
            grain, glow, vignette,
            rotation, resize_pct, letterbox_ratio
        )

        # Badges
        badge_html = ""
        if selected_profile != "— Sin Perfil —":
            badge_html += f"<span class='profile-badge'>✦ {selected_profile}</span>"
        if letterbox_ratio != "— Sin barras —":
            ratio_short = letterbox_ratio.split(" ")[0]
            badge_html += f"<span class='bars-badge'>▬ {ratio_short}</span>"
        if badge_html:
            st.markdown(badge_html, unsafe_allow_html=True)

        # Comparacion
        col1, col2 = st.columns(2, gap="medium")
        with col1:
            st.markdown("<span class='img-label'>Original</span>", unsafe_allow_html=True)
            st.image(img_orig, use_container_width=True)
        with col2:
            st.markdown("<span class='img-label'>Resultado</span>", unsafe_allow_html=True)
            st.image(img_mod, use_container_width=True)

        # Metadata
        with st.expander("📊 Informacion de imagen", expanded=False):
            w_o, h_o = img_orig.size
            w_m, h_m = img_mod.size
            c1, c2, c3, c4, c5, c6 = st.columns(6)
            c1.metric("Original",  f"{w_o}×{h_o}")
            c2.metric("Resultado", f"{w_m}×{h_m}")
            c3.metric("Grano",     f"{int(grain*100)}%")
            c4.metric("Glow",      f"{int(glow*100)}%")
            c5.metric("Vineta",    f"{int(vignette*100)}%")
            ratio_display = letterbox_ratio.split(" ")[0] if letterbox_ratio != "— Sin barras —" else "Libre"
            c6.metric("Formato",   ratio_display)

        # Exportacion
        st.divider()
        st.subheader("💾 Exportar")
        exp_q = st.slider("Calidad JPEG", 70, 100, 95, 1)
        safe = selected_profile.replace(" ", "_").replace("·", "").replace(":", "").replace("/", "").replace("(", "").replace(")", "")

        dcol1, dcol2, dcol3 = st.columns(3)
        with dcol1:
            st.download_button(
                "🌈 Exportar · Color",
                data=image_to_bytes(img_mod, exp_q),
                file_name=f"SRP_{safe}_{uploaded_file.name}.jpg",
                mime="image/jpeg", use_container_width=True
            )
        with dcol2:
            img_bw = ImageEnhance.Contrast(ImageOps.grayscale(img_mod)).enhance(1.2).convert("RGB")
            st.download_button(
                "⬛ Exportar · B&N",
                data=image_to_bytes(img_bw, exp_q),
                file_name=f"SRP_BW_{safe}_{uploaded_file.name}.jpg",
                mime="image/jpeg", use_container_width=True
            )
        with dcol3:
            st.download_button(
                "📁 Original sin editar",
                data=image_to_bytes(img_orig, 98),
                file_name=f"original_{uploaded_file.name}.jpg",
                mime="image/jpeg", use_container_width=True
            )

else:
    st.markdown("""
    <div style="text-align:center;padding:60px 20px;border:1px dashed #2a2a2d;border-radius:12px;margin-top:20px">
        <div style="font-size:3rem;margin-bottom:16px">🎬</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;color:#e8d5a3;letter-spacing:-0.02em">
            Sube una imagen para comenzar
        </div>
        <div style="font-size:0.75rem;color:#6b6965;margin-top:8px;letter-spacing:0.08em">
            JPG · PNG · DNG · CR2 · NEF · ARW · HEIC — RAW nativo soportado
        </div>
        <div style="font-size:0.7rem;color:#3a3a3d;margin-top:20px;letter-spacing:0.05em">
            70+ perfiles &nbsp;·&nbsp; Grano analogico &nbsp;·&nbsp; Glow &nbsp;·&nbsp; Vineta &nbsp;·&nbsp; Letterbox 9 formatos
        </div>
    </div>
    """, unsafe_allow_html=True)
