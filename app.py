from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64
import toml


def generate_image(prompt):
    """
    Generates an image based on the given prompt using the Gemini API.

    Args:
        prompt: The text prompt to generate the image from.

    Returns:
        A PIL Image object, or None if an error occurred.
    """
    try:
        # Load the secrets from the .streamlit/secrets.toml file
        secrets = toml.load(".streamlit/secrets.toml")
        api_key = secrets["GEMINI_API_KEY"]

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-2.0-flash-exp-image-generation",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=['Text', 'Image']
            )
        )

        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                image_data = base64.b64decode(part.inline_data.data)
                image = Image.open(BytesIO(image_data))
                return image
        return None  # No image data found in the response

    except Exception as e:
        print(f"Error generating image: {e}")
        return None


if __name__ == '__main__':
    prompt = ('Hi, can you create a 3d rendered image of a horse '
              'with wings and a top hat flying over a happy '
              'futuristic scifi city with lots of greenery?')

    image = generate_image(prompt)

    if image:
        image.save('gemini-native-image.png')
        image.show()
    else:
        print("No image was generated.")