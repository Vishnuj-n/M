import streamlit as st
from PIL import Image
from main import Meme
from io import BytesIO
import base64


st.title("AI Meme Generator")
# streamlit_app.py
import streamlit as st
from PIL import Image
from main import Meme

st.title("AI Meme Generator")

# Optional API key input
with st.sidebar.expander("API Settings (Optional)", expanded=False):
    user_api_key = st.text_input("Enter your OpenAI API Key:", type="password",
                                help="Leave empty to use the default API key")

# Initialize Meme class with user API key if provided
if 'user_api_key' in locals() and user_api_key:
    meme_generator = Meme(key=st.secrets["OPENAI_API_KEY"], user_api_key=user_api_key)
else:
    meme_generator = Meme(key=st.secrets["OPENAI_API_KEY"])

# Store generated image in session state
if 'generated_image' not in st.session_state:
    st.session_state.generated_image = None

# User inputs
prompt = st.text_input("Enter a prompt for image generation:")
text = st.text_area("Enter meme text:")
position = st.selectbox("Select text position:", ["top", "center", "bottom"], index=2)

if st.button("Generate Image"):
    if prompt:
        with st.spinner("Generating image..."):
            image = meme_generator.generate_image(prompt)
            if image:
                st.session_state.generated_image = image
                st.image(image, caption="Generated Image", use_container_width=True)
            else:
                st.error("Failed to generate image.")
    else:
        st.warning("Please enter a prompt for image generation.")

if st.button("Add Text to Meme"):
    if st.session_state.generated_image and text:
        with st.spinner("Adding text to image..."):
            try:
                meme = meme_generator.add_text(st.session_state.generated_image, text, position)
                st.image(meme, caption="Final Meme", use_container_width=True)
                st.success("Meme generated successfully")
                
                # Add download button for the meme
                buffered = BytesIO()
                meme.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                href = f'<a href="data:file/png;base64,{img_str}" download="ai_meme.png">Download Meme</a>'
                st.markdown(href, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")
    elif not st.session_state.generated_image:
        st.warning("Please generate an image first.")
    else:
        st.warning("Please enter text for the meme.")

