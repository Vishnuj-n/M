import streamlit as st
from PIL import Image
from main import Meme

# Initialize Meme class
meme_generator = Meme()

st.title("AI Meme Generator")

# User inputs
prompt = st.text_input("Enter a prompt for image generation:")
text = st.text_area("Enter meme text:")
position = st.selectbox("Select text position:", ["top", "center", "bottom"], index=2)

if st.button("Generate Meme"):
    if prompt:
        with st.spinner("Generating image..."):
            image = meme_generator.generate_image(prompt)
            if image:
                st.image(image, caption="Generated Image",  use_container_width=True)
            else:
                st.error("Failed to generate image.")
    else:
        st.warning("Please enter a prompt for image generation.")

if st.button("Add Text to Meme"):
    if text:
        with st.spinner("Adding text to image..."):
            try:
                image1=Image.open("gemini-native-image.png")
                if image1.mode != 'RGBA':
                    image1 = image1.convert('RGBA')
                meme = meme_generator.add_text(image1,text, position)
                st.image(meme, caption="Final Meme", use_container_width =True)
                #meme_generator.save_meme("final_meme.png")
                st.success("Meme saved as final_meme.png")
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please enter text for the meme.")
