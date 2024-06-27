# views.py

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import os
import requests
import base64
from PIL import Image, ImageDraw, ImageFont
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def meme_input(request):
    return render(request, "meme.html")

def generate_meme(request):
    if request.method == "POST":
        about_meme = request.GET.get("about_meme")
        image_name = "image_name"  

        try:
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

            model = genai.GenerativeModel("gemini-pro")
            chat = model.start_chat(history=[])
            instruction = "You are a funny meme generator."
            
            famous_memes = [
                "Grumpy Cat", "Success Kid", "Doge", "Bad Luck Brian",
                "Distracted Boyfriend", "Hide the Pain Harold"
            ]
            
            question = f"Generate me a text prompt for an image of a funny meme. It should be related to {about_meme}. There should be no text in the image and there should be space for text at the bottom."
            response = chat.send_message(instruction + question)

            engine_id = "stable-diffusion-v1-6"
            api_host = os.getenv('API_HOST', 'https://api.stability.ai')

            image_response = requests.post(
                f"{api_host}/v1/generation/{engine_id}/text-to-image",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": f"Bearer {os.getenv('STABILITY_API_KEY')}"
                },
                json={
                    "text_prompts": [{"text": response.text}],
                    "cfg_scale": 7,
                    "height": 512,
                    "width": 1024,
                    "samples": 1,
                    "steps": 30,
                },
            )
            image_response.raise_for_status()
            data = image_response.json()

            for i, image in enumerate(data["artifacts"]):
                image_path = f"static/images/{image_name}.png"
                with open(image_path, "wb") as f:
                    f.write(base64.b64decode(image["base64"]))

            my_image = Image.open(image_path)

            font_size = 40
            try:
                title_font = ImageFont.truetype("meme_font.ttf", font_size)
            except IOError:
                title_font = ImageFont.load_default(font_size)

            img = Image.open(f'{image_name}.png')

            image_to_text_model = genai.GenerativeModel('gemini-1.5-flash')
            text_from_image = image_to_text_model.generate_content(img)

            question2 = f"Generate a short and funny text for a meme, which image can be described as {text_from_image}. The meme text should be heavily related to the image and iy should be very funny. Please note that the text can't be longer than 40 characters. Please note that the text should not be sexual in any way. The text should only be the text so ho **Text** before the image text. There should be no image description in the text, only the the funny text for the meme."
            response2 = chat.send_message(instruction + question2)

            title_text = response2.text.upper()
            image_editable = ImageDraw.Draw(my_image)

            text_color = (255, 255, 255)
            outline_color = (0, 0, 0)
            outline_width = 2

            draw_text_with_outline(image_editable, title_text, title_font, text_color, outline_color, outline_width, my_image)

            my_image.save(image_path)

        except requests.exceptions.RequestException as e:
            return JsonResponse({"status": "error", "message": str(e)})


            return JsonResponse({"status": "error", "message": str(e)})

        return render(request, "final/final_meme.html")
    else:
        return HttpResponse("<h1>Hey, sorry something whent wrong. Please try again and relode the page.</h1>")

def draw_text_with_outline(draw, text, font, text_color, outline_color, outline_width, image):
    image_width, image_height = image.size
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    if text_width > image_width - 40:
        words = text.split()
        half = len(words) // 2
        first_line = ' '.join(words[:half])
        second_line = ' '.join(words[half:])

        bbox_first = draw.textbbox((0, 0), first_line, font=font)
        bbox_second = draw.textbbox((0, 0), second_line, font=font)
        text_width_first = bbox_first[2] - bbox_first[0]
        text_width_second = bbox_second[2] - bbox_second[0]
        text_height = bbox_first[3] - bbox_first[1] + bbox_second[3] - bbox_second[1] + 10

        top_x_position_first = (image_width - text_width_first) / 2
        top_x_position_second = (image_width - text_width_second) / 2
        top_y_position = image_height - text_height - 20

        draw_text(draw, first_line, (top_x_position_first, top_y_position), font, text_color, outline_color, outline_width)
        draw_text(draw, second_line, (top_x_position_second, top_y_position + bbox_first[3] - bbox_first[1] + 10), font, text_color, outline_color, outline_width)
    else:
        bottom_x_position = (image_width - text_width) / 2
        bottom_y_position = image_height - text_height - 20

        draw_text(draw, text, (bottom_x_position, bottom_y_position), font, text_color, outline_color, outline_width)

def draw_text(draw, text, position, font, text_color, outline_color, outline_width):
    x, y = position
    for offset in [(outline_width, 0), (-outline_width, 0), (0, outline_width), (0, -outline_width),
                   (outline_width, outline_width), (-outline_width, -outline_width),
                   (-outline_width, outline_width), (outline_width, -outline_width)]:
        draw.text((x + offset[0], y + offset[1]), text, font=font, fill=outline_color)
    draw.text((x, y), text, font=font, fill=text_color)
