from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.core.files.storage import default_storage
from dotenv import load_dotenv
import os
from PIL import Image
import pytesseract
from pytesseract import TesseractNotFoundError
import google.generativeai as genai


#Final joke

response_text = "This is a funny joke!"

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

def joke_home(request):
    return render(request, "joke.html")

# Configure generative AI model
def configure_model():
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")
    chat = model.start_chat(history=[])
    instruction = "In this chat, you should be a funny joke maker."
    return chat, instruction

def generate(request):
    if request.method == "POST":
        category = request.POST.get("category", "")
        insider = request.POST.get("inside", "")
    
        chat, instruction = configure_model()
        question = f"Make a joke in the category {category} about {insider} please."
        response = chat.send_message(instruction + question)
        response_text = response.text

        content = {"response_text": response_text}
        return render(request, "final/final_joke.html", content)
    return HttpResponse("<h1>Hey, sorry something whent wrong. Please try again and relode the page.</h1>")

def generate_from_image(request):
    if request.method == "POST" and request.FILES.get("image"):
        image = request.FILES["image"]
        if image.name[-4:] != ".png" or ".jpg":
            print("No image")
        description = request.POST.get("description", "")
        image_path = default_storage.save(image.name, image)

        try:
            img = Image.open(default_storage.path(image_path))
            extracted_text = pytesseract.image_to_string(img)
        except TesseractNotFoundError:
            return HttpResponseBadRequest("Tesseract is not installed or not in your PATH.")
        except Exception as e:
            return HttpResponseBadRequest(f"An error occurred while processing the image: {str(e)}")

        chat, instruction = configure_model()
        question = f"Make a joke about the following image description: {extracted_text} and the user-provided description: {description}."
        response = chat.send_message(instruction + question)
        response_text = response.text

        content = {"response_text": response_text}
        return render(request, "final/final_joke.html", content)
    
    return render(request, "index.html")
