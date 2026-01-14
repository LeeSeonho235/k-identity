from fastapi.responses import FileResponse 
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import openai
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini 설정 (SDK 방식에 맞춰 수정)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/")
async def read_index():
    return FileResponse('index.html')

@app.get("/generate-k-identity")
async def generate_k_identity(english_name: str, vibe: str, gender: str, lang: str, strategy: str):
    # 1. Gemini로 이름 및 설명 생성
    text_prompt = f"Suggest 1 Korean name for a {gender} named '{english_name}' with a '{vibe}' vibe based on {strategy}. Answer in {lang}. Line 1: Name(Hanja), Line 2: Meaning, Line 3: Explanation."
    
    model = genai.GenerativeModel("gemini-1.5-flash")
    text_response = model.generate_content(text_prompt)
    lines = text_response.text.strip().split('\n')
    
    # 2. DALL-E로 이미지 생성 (URL만 가져오기)
    dalle_prompt = f"A stylish K-pop {gender} portrait, inspired by the name '{lines[0]}'. Vibe: {vibe}."
    response = openai_client.images.generate(
        model="dall-e-3",
        prompt=dalle_prompt,
        n=1
    )
    final_image_url = response.data[0].url # 파일을 저장하지 않고 주소만 씁니다!

    return {
        "korean_name": lines[0] if len(lines) > 0 else "Error",
        "hanja_meaning": lines[1] if len(lines) > 1 else "",
        "explanation": lines[2] if len(lines) > 2 else text_response.text,
        "image_url": final_image_url
    }