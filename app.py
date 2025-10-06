import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageEnhance
from io import BytesIO

st.set_page_config(page_title="Image Filters", layout="wide")
st.title("Image Filters")

# --- Session state ---
if "image_bytes" not in st.session_state:
    st.session_state.image_bytes = None
if "mode" not in st.session_state:
    st.session_state.mode = None

# --- Mode selection buttons ---
st.markdown("<h4 style='text-align:center;'>Select Input Mode</h4>", unsafe_allow_html=True)
col1, col2 = st.columns([1,1])
with col1:
    if st.button("Upload An Image", use_container_width=True):
        st.session_state.mode = "upload"
with col2:
    if st.button("Live Image", use_container_width=True):
        st.session_state.mode = "camera"

mode = st.session_state.get("mode", None)

# --- Image input ---
if mode == "upload":
    file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if file:
        st.session_state.image_bytes = file.read()
elif mode == "camera":
    img_file = st.camera_input("Take a photo")
    if img_file:
        st.session_state.image_bytes = img_file.getvalue()

# --- Display & filter controls ---
if st.session_state.image_bytes:
    image = Image.open(BytesIO(st.session_state.image_bytes)).convert("RGB")
    st.markdown("---")
    st.subheader("Filters & Adjustments")

    # Sliders and filter select in an expander
    with st.expander("Adjustments"):
        filter_name = st.selectbox("Choose Filter:", [
            "Grayscale", "Paris", "London", "Tokyo", "Oslo"
        ])
        brightness = st.slider("Brightness", 0.5, 2.0, 1.0, step=0.05)
        scale = st.slider("Scale", 0.5, 1.5, 1.0, step=0.05)

    # --- Side-by-side display ---
    col_orig, col_filtered = st.columns(2)
    with col_orig:
        st.markdown("**Original Image**")
        st.image(image, use_container_width=True)
    with col_filtered:
        st.markdown("**Filtered Image**")
        img_cv = np.array(image)

        # Apply filters (without affecting color on scale)
        if filter_name == "Grayscale":
            img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)
            img_cv = cv2.cvtColor(img_cv, cv2.COLOR_GRAY2RGB)
        elif filter_name == "Paris":
            img_cv = cv2.convertScaleAbs(img_cv, alpha=1.2, beta=0) 
            img_cv = cv2.applyColorMap(img_cv, cv2.COLORMAP_PINK)
        elif filter_name == "London":
            img_cv = cv2.convertScaleAbs(img_cv, alpha=0.9, beta=0)
            img_cv = cv2.applyColorMap(img_cv, cv2.COLORMAP_WINTER)
        elif filter_name == "Tokyo":
            img_cv = cv2.convertScaleAbs(img_cv, alpha=1.3, beta=0)
            img_cv = cv2.applyColorMap(img_cv, cv2.COLORMAP_HOT)
        elif filter_name == "Oslo":
            img_cv = cv2.convertScaleAbs(img_cv, alpha=0.8, beta=0)
            img_cv = cv2.applyColorMap(img_cv, cv2.COLORMAP_BONE)
        img_pil = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))

        # Apply brightness & scale
        enhancer = ImageEnhance.Brightness(img_pil)
        img_pil = enhancer.enhance(brightness)
        w, h = img_pil.size
        img_pil = img_pil.resize((int(w * scale), int(h * scale)))
        st.image(img_pil, caption=f"{filter_name} Filter", use_container_width=True)

        # Download button
        buf = BytesIO()
        img_pil.save(buf, format="PNG")
        byte_im = buf.getvalue()
        st.download_button(
            "Download Filtered Image",
            data=byte_im,
            file_name=f"{filter_name.lower()}.png",
            mime="image/png"
        )
else:
    st.info("Upload or capture an image to start")
