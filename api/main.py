from fastapi.responses import FileResponse 
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import google.generativeai as genai
import openai
from dotenv import load_dotenv
import uuid
import requests

load_dotenv()
app = FastAPI()

if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/")
async def read_index():
    return FileResponse('index.html') # 접속 시 index.html을 보여줍니다

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_dalle_image(prompt_text, filename):
    try:
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=prompt_text,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        img_data = requests.get(image_url).content
        file_path = f"static/{filename}"
        with open(file_path, "wb") as f:
            f.write(img_data)
        return f"http://127.0.0.1:8000/{file_path}"
    except Exception as e:
        print(f"DALL-E 3 Error: {e}")
        return "https://via.placeholder.com/512x512.png?text=Image+Error"

@app.get("/generate-k-identity")
async def generate_k_identity(english_name: str, vibe: str, gender: str, lang: str, strategy: str):
    # 전략과 언어에 따른 맞춤 프롬프트
    text_prompt = f"""
    Suggest 1 best Korean name for a {gender} named '{english_name}' with a '{vibe}' vibe.
    Constraint: Base the name on {strategy} (sound or meaning).
    
    IMPORTANT: Write the entire output in {lang} language (except the Korean name itself).
    Line 1: Name in Hangeul (Hanja)
    Line 2: Hanja meanings in {lang}
    Line 3: One poetic explanation in {lang}
    """
    
    text_response = gemini_client.models.generate_content(model="gemini-2.5-flash", contents=text_prompt)
    lines = text_response.text.strip().split('\n')
    
    k_name_hanja = lines[0] if len(lines) > 0 else "Error"
    hanja_meaning = lines[1] if len(lines) > 1 else ""
    explanation = lines[2] if len(lines) > 2 else text_response.text

    # DALL-E 이미지 프롬프트에 성별 반영
    dalle_prompt = f"A stylish K-pop {gender} portrait, inspired by the name '{k_name_hanja}'. Vibe: {vibe}. High-quality photography."
    
    image_filename = f"{uuid.uuid4()}.png"
    final_image_url = generate_dalle_image(dalle_prompt, image_filename)

    return {
        "korean_name": k_name_hanja,
        "hanja_meaning": hanja_meaning,
        "explanation": explanation,
        "image_url": final_image_url,
        "english_name_original": english_name
    }