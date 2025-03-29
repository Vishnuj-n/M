from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO
import toml
from google.genai import genai
from google.genai import types

class Meme:
    def __init__(self, secrets_file=".streamlit/secrets.toml"):
        self.secrets = toml.load(secrets_file)
        self.api_key = self.secrets["GEMINI_API_KEY"]
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-2.0-flash-exp-image-generation"


    def generate_image(self,prompt):
        prompt_t=(prompt)

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt_t,
            config=types.GenerateContentConfig(
            response_modalities=['Text', 'Image']
        )
    )
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                print(part.text)
            elif part.inline_data is not None:
                image = Image.open(BytesIO((part.inline_data.data)))
                image.save('gemini-native-image.png')
                return image
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

        except FileNotFoundError:
            raise FileNotFoundError(f"Image file not found")
        except Exception as e:
            raise Exception(f"Error processing image: {str(e)}")
