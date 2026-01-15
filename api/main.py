from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from google import genai
import openai
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/")
async def read_index():
    return FileResponse('index.html')

# 1단계: 이름만 생성 (빠름)
@app.get("/api/get-name")
async def get_name(english_name: str, vibe: str, gender: str, lang: str, strategy: str):
    try:
        text_prompt = f"Suggest 1 Korean name for a {gender} named '{english_name}'. Vibe: {vibe}. Strategy: {strategy}. Answer in {lang}."
        response = gemini_client.models.generate_content(model="gemini-1.5-flash", contents=text_prompt)
        
        lines = response.text.strip().split('\n')
        return {
            "korean_name": lines[0] if len(lines) > 0 else "Error",
            "hanja_meaning": lines[1] if len(lines) > 1 else "",
            "explanation": lines[2] if len(lines) > 2 else response.text
        }
    except Exception as e:
        return {"error": str(e)}, 500

# 2단계: 이미지 생성 (DALL-E 3 호출, 약 10초 소요)
@app.get("/api/get-image")
async def get_image(k_name: str, gender: str, vibe: str):
    try:
        dalle_prompt = f"A stylish K-pop {gender} portrait, inspired by the name '{k_name}'. Vibe: {vibe}."
        img_response = openai_client.images.generate(model="dall-e-3", prompt=dalle_prompt, n=1)
        return {"image_url": img_response.data[0].url}
    except Exception as e:
        return {"error": str(e)}, 500