# main.py
from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO
from openai import OpenAI
import streamlit as st
import requests

class Meme:
    def __init__(self, key, user_api_key=None):  
        # Use user provided API key if available, otherwise use from secrets
        if user_api_key and user_api_key.strip():
            self.api_key = user_api_key
        else:
            self.api_key = key
        
        self.client = OpenAI(api_key=self.api_key)

    def generate_image(self, prompt):
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            # Convert the image URL to a PIL image
            image_url = response.data[0].url
            image_response = requests.get(image_url, stream=True)
            image = Image.open(BytesIO(image_response.content))
            
            return image
        except Exception as e:
            st.error(f"Error generating image: {str(e)}")
            return None

    def add_text(self, image, text, position='bottom'):
        try:
            if image.mode != 'RGBA':
                image = image.convert('RGBA')

            blank_image = Image.new("RGBA", image.size)
            draw = ImageDraw.Draw(blank_image)

            font_path = "impact/impact.ttf"
            font_size = 50
            text_color = "white"
            shadow_offset = (4, 4)
            shadow_color = "black"

            try:
                font = ImageFont.truetype(font_path, font_size)
            except OSError:
                print(f"Warning: Could not load {font_path}. Using default font.")
                font = ImageFont.load_default()

            lines = text.split("\n")
            line_heights = [
                draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1]
                for line in lines
            ]
            text_height = sum(line_heights)

            if position == 'top':
                y_start = image.height // 8
            elif position == 'center':
                y_start = (image.height - text_height) // 2
            else:
                y_start = image.height - text_height - image.height // 6

            shadow_y = y_start
            for line, height in zip(lines, line_heights):
                text_width = draw.textbbox((0, 0), line, font=font)[2] - draw.textbbox((0, 0), line, font=font)[0]
                text_x = (image.width // 2) - text_width // 2 + shadow_offset[0]
                shadow_position = (text_x, shadow_y + shadow_offset[1])
                draw.text(shadow_position, line, fill=shadow_color, font=font)
                shadow_y += height

            text_y = y_start
            for line, height in zip(lines, line_heights):
                text_width = draw.textbbox((0, 0), line, font=font)[2] - draw.textbbox((0, 0), line, font=font)[0]
                text_x = (image.width // 2) - text_width // 2
                text_position = (text_x, text_y)
                draw.text(text_position, line, fill=text_color, font=font)
                text_y += height

            final_image = Image.alpha_composite(image, blank_image)
            return final_image

        except Exception as e:
            raise Exception(f"Error processing image: {str(e)}")