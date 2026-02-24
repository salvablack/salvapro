import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageStat
import rawpy
import os
import numpy as np
from pillow_heif import register_heif_opener
import io

# Configuración de la página
st.set_page_config(page_title="Salva Rosales Raw PRO", layout="wide")
register_heif_opener()

# ==================================================
# LÓGICA DE FILTROS CINEMATOGRÁFICOS
# ==================================================
def apply_cinema_profile(image, profile_name):
    if profile_name == "Ninguno":
        return image
    
    img = image.convert("RGB")
    
    # Definición de perfiles (Ajustes: Contraste, Color, Brillo, Tinte R, G, B)
    profiles = {
        # --- CLÁSICOS Y CINE ---
        "Blockbuster (Teal & Orange)": {"c": 1.2, "s": 1.3, "rgb": (1.1, 1.0, 0.9)},
        "Noir Classic": {"c": 1.5, "s": 0.0, "rgb": (1.0, 1.0, 1.0)},
        "Vintage 70s": {"c": 0.9, "s": 0.8, "rgb": (1.2, 1.1, 0.8)},
        "Technicolor": {"c": 1.4, "s": 1.6, "rgb": (1.0, 1.0, 1.0)},
        "Kodak Portra 400": {"c": 1.1, "s": 1.1, "rgb": (1.1, 1.05, 0.95)},
        "Fuji Velvia": {"c": 1.3, "s": 1.5, "rgb": (0.9, 1.1, 1.0)},
        "Wes Anderson (Pinkish)": {"c": 0.9, "s": 1.2, "rgb": (1.2, 0.9, 1.0)},
        "Cyberpunk": {"c": 1.3, "s": 1.4, "rgb": (1.2, 0.8, 1.3)},
        "Western": {"c": 1.2, "s": 0.7, "rgb": (1.2, 1.1, 0.8)},
        "Moonlight (Blue Tint)": {"c": 1.1, "s": 0.9, "rgb": (0.8, 0.9, 1.3)},
        
        # --- ESTILOS MODERNOS ---
        "Moody Dark": {"c": 1.4, "s": 0.7, "rgb": (0.8, 0.8, 0.8)},
        "High Key Bright": {"c": 0.8, "s": 1.1, "rgb": (1.1, 1.1, 1.1)},
        "Muted Tones": {"c": 1.0, "s": 0.4, "rgb": (1.0, 1.0, 1.0)},
        "Deep Ocean": {"c": 1.2, "s": 1.2, "rgb": (0.7, 1.0, 1.2)},
        "Warm Sunset": {"c": 1.1, "s": 1.3, "rgb": (1.3, 1.0, 0.8)},
        "Cold Winter": {"c": 1.0, "s": 0.8, "rgb": (0.9, 1.0, 1.2)},
        "Sepia Nostalgia": {"c": 1.1, "s": 0.5, "rgb": (1.2, 1.0, 0.7)},
        "Urban Green": {"c": 1.2, "s": 1.1, "rgb": (0.9, 1.2, 1.0)},
        "Golden Hour": {"c": 1.1, "s": 1.4, "rgb": (1.2, 1.1, 0.7)},
        "Matrix (Greenish)": {"c": 1.2, "s": 1.1, "rgb": (0.8, 1.3, 0.8)},

        # --- ADICIONALES (Hasta completar 40) ---
        "Kodak Ektar": {"c": 1.3, "s": 1.5, "rgb": (1.1, 1.0, 0.9)},
        "Agfa Vista": {"c": 1.2, "s": 1.2, "rgb": (1.0, 1.0, 1.1)},
        "B&W Dramatic": {"c": 1.8, "s": 0.0, "rgb": (1.0, 1.0, 1.0)},
        "Faded Film": {"c": 0.8, "s": 0.7, "rgb": (1.0, 1.0, 1.0)},
        "Polaroid": {"c": 0.9, "s": 0.8, "rgb": (1.1, 1.1, 1.0)},
        "Cinema Blue": {"c": 1.1, "s": 1.1, "rgb": (0.9, 1.0, 1.3)},
        "Forest Tale": {"c": 1.1, "s": 1.2, "rgb": (0.9, 1.3, 0.9)},
        "Pastel Dream": {"c": 0.8, "s": 0.9, "rgb": (1.1, 1.1, 1.2)},
        "Neon Night": {"c": 1.4, "s": 1.6, "rgb": (1.1, 0.7, 1.4)},
        "Crimson": {"c": 1.2, "s": 1.1, "rgb": (1.4, 0.8, 0.8)},
        "Olive Grove": {"c": 1.0, "s": 1.1, "rgb": (1.1, 1.2, 0.9)},
        "Retro Digital": {"c": 1.1, "s": 1.3, "rgb": (1.0, 1.2, 1.1)},
        "Soft Glow": {"c": 0.9, "s": 1.1, "rgb": (1.0, 1.0, 1.0)},
        "Vibrant Nature": {"c": 1.2, "s": 1.7, "rgb": (1.0, 1.1, 1.0)},
        "Bleach Bypass": {"c": 1.6, "s": 0.4, "rgb": (1.0, 1.0, 1.0)},
        "Silky Smooth": {"c": 0.9, "s": 0.9, "rgb": (1.05, 1.05, 1.05)},
        "Night Vision": {"c": 1.3, "s": 1.0, "rgb": (0.5, 1.5, 0.5)},
        "Royal Gold": {"c": 1.2, "s": 1.2, "rgb": (1.3, 1.2, 0.8)},
        "Shadow Crush": {"c": 1.5, "s": 0.9, "rgb": (0.9, 0.9, 0.9)},
        "High Contrast": {"c": 2.0, "s": 1.2, "rgb": (1.0, 1.0, 1.0)}
    }

    p = profiles.get(profile_name)
    
    # Aplicar ajustes
    img = ImageEnhance.Contrast(img).enhance(p["c"])
    img = ImageEnhance.Color(img).enhance(p["s"])
    
    # Aplicar tinte RGB
    r, g, b = img.split()
    r = r.point(lambda i: i * p["rgb"][0])
    g = g.point(lambda i: i * p["rgb"][1])
    b = b.point(lambda i: i * p["rgb"][2])
    
    return Image.merge("RGB", (r, g, b))

# --- Resto de funciones (Gamma, Focus, etc.) ---
def load_image(file_bytes, file_name):
    ext = os.path.splitext(file_name)[1].lower()
    if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.heic', '.heif']:
        return Image.open(file_bytes)
    elif ext in ['.dng', '.cr2', '.nef', '.arw']:
        with rawpy.imread(file_bytes) as raw:
            rgb = raw.postprocess()
        return Image.fromarray(rgb)
    return None

def apply_gamma(image, gamma):
    if gamma == 1.0: return image
    arr = np.array(image)
    arr = np.clip((arr / 255.0) ** (1.0 / gamma) * 255, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)

def apply_focus(image, amount):
    if amount <= 0: return image
    return image.filter(ImageFilter.UnsharpMask(radius=2, percent=int(amount * 100), threshold=3))

# ==================================================
# INTERFAZ STREAMLIT
# ==================================================
st.title("📷 Salva Raw PRO - Cinematic Edition")

with st.sidebar:
    st.header("Controles")
    st.markdown("[💖 Donar (PayPal)](https://www.paypal.com/donate/?hosted_button_id=GWJTR9XF6JSY8)")
    st.divider()
    
    # Selector de Perfil Cinematográfico
    perfil_list = ["Ninguno", "Blockbuster (Teal & Orange)", "Noir Classic", "Vintage 70s", "Technicolor", 
                   "Kodak Portra 400", "Fuji Velvia", "Wes Anderson (Pinkish)", "Cyberpunk", "Western", 
                   "Moonlight (Blue Tint)", "Moody Dark", "High Key Bright", "Muted Tones", "Deep Ocean", 
                   "Warm Sunset", "Cold Winter", "Sepia Nostalgia", "Urban Green", "Golden Hour", 
                   "Matrix (Greenish)", "Kodak Ektar", "Agfa Vista", "B&W Dramatic", "Faded Film", 
                   "Polaroid", "Cinema Blue", "Forest Tale", "Pastel Dream", "Neon Night", "Crimson", 
                   "Olive Grove", "Retro Digital", "Soft Glow", "Vibrant Nature", "Bleach Bypass", 
                   "Silky Smooth", "Night Vision", "Royal Gold", "Shadow Crush", "High Contrast"]
    
    selected_profile = st.selectbox("Perfil Cinematográfico", perfil_list)
    
    st.divider()
    gamma = st.number_input("Gamma", min_value=0.1, max_value=3.0, value=1.0, step=0.05)
    focus = st.number_input("Focus (Enfoque)", min_value=0.0, max_value=10.0, value=0.0, step=0.1)
    rotation = st.number_input("Rotación (Grados)", min_value=-360, max_value=360, value=0, step=90)
    resize_pct = st.number_input("Redimensionar %", min_value=1, max_value=100, value=100, step=1)

uploaded_file = st.file_uploader("Seleccionar Imagen", type=["jpg", "jpeg", "png", "dng", "cr2", "nef", "arw", "heic"])

if uploaded_file:
    img_orig = load_image(uploaded_file, uploaded_file.name)
    
    if img_orig:
        # 1. Aplicar Perfil Cinematográfico seleccionado
        img_mod = apply_cinema_profile(img_orig, selected_profile)
        
        # 2. Aplicar Ajustes Manuales
        if rotation != 0:
            img_mod = img_mod.rotate(rotation, expand=True)
        img_mod = apply_gamma(img_mod, gamma)
        img_mod = apply_focus(img_mod, focus)
        
        if resize_pct < 100:
            w, h = img_mod.size
            img_mod = img_mod.resize((int(w * resize_pct / 100), int(h * resize_pct / 100)), Image.Resampling.LANCZOS)

        # 3. Visualización
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original")
            st.image(img_orig, use_container_width=True)
        with col2:
            st.subheader(f"Perfil: {selected_profile}")
            st.image(img_mod, use_container_width=True)

        # 4. Exportación
        st.divider()
        exp_col1, exp_col2 = st.columns(2)

        with exp_col1:
            buf_color = io.BytesIO()
            img_mod.save(buf_color, format="JPEG", quality=95)
            st.download_button("🌈 Exportar en Color", buf_color.getvalue(), f"color_{selected_profile}_{uploaded_file.name}.jpg", "image/jpeg", use_container_width=True)

        with exp_col2:
            img_bw = ImageOps.grayscale(img_mod)
            # Un toque extra de contraste para el B&N exportado
            img_bw = ImageEnhance.Contrast(img_bw).enhance(1.2)
            buf_bw = io.BytesIO()
            img_bw.save(buf_bw, format="JPEG", quality=95)
            st.download_button("⚪ Exportar en Blanco y Negro", buf_bw.getvalue(), f"BW_{selected_profile}_{uploaded_file.name}.jpg", "image/jpeg", use_container_width=True)
else:
    st.info("Sube una imagen para aplicar los perfiles.")
