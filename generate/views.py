from django.shortcuts import render
from django.http import JsonResponse
import google.generativeai as genai
from dotenv import load_dotenv, dotenv_values
import os

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
def home(request):
    return render(request, "index.html")

def generate(request):
    category = request.GET["categoryer"]
    insider = request.GET["inside"]

    genai.configure(
        api_key=api_key
    )

    model = genai.GenerativeModel("gemini-pro")
    chat = model.start_chat(history=[])
    instruction = "In this chat, you should be a funny joke maker."

    question = f"Make a joke in the category {category} about {insider} please."
    response = chat.send_message(instruction + question)

    response_text = response.text

    content = {"response_text": response_text}
    return render(request, "joke.html", content)

# New API view
def generate_api(request):
    category = request.GET.get("categoryer", "")
    insider = request.GET.get("inside", "")

    genai.configure(
        api_key=api_key
    )

    model = genai.GenerativeModel("gemini-pro")
    chat = model.start_chat(history=[])
    instruction = "In this chat, you should be a funny joke maker."

    question = f"Make a joke in the category {category} about {insider} please."
    response = chat.send_message(instruction + question)

    response_text = response.text

    return JsonResponse({"response_text": response_text})
