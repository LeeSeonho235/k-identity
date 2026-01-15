from fastapi.responses import FileResponse 
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google import genai  # 최신 라이브러리 임포트 방식
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

# 클라이언트 설정
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/")
async def read_index():
    # 루트 접속 시 같은 폴더나 상위의 index.html을 반환
    return FileResponse('index.html')

@app.get("/api/generate-k-identity")
async def generate_k_identity(english_name: str, vibe: str, gender: str, lang: str, strategy: str):
    # 1. Gemini 이름 생성
    text_prompt = f"Suggest 1 Korean name for a {gender} named '{english_name}' with a '{vibe}' vibe based on {strategy}. Answer in {lang}. Line 1: Name(Hanja), Line 2: Meaning, Line 3: Explanation."
    
    
    response = gemini_client.models.generate_content(model="models/gemini-1.5-flash", contents=text_prompt)
    lines = response.text.strip().split('\n')
    
    # 2. DALL-E 이미지 생성 (저장하지 않고 URL만 반환)
    dalle_prompt = f"A stylish K-pop {gender} portrait, inspired by the name '{lines[0]}'. Vibe: {vibe}."
    img_response = openai_client.images.generate(
        model="dall-e-3",
        prompt=dalle_prompt,
        n=1
    )
    # Vercel은 파일을 저장할 수 없으므로, OpenAI가 준 임시 URL을 그대로 씁니다.
    final_image_url = img_response.data[0].url

    return {
        "korean_name": lines[0] if len(lines) > 0 else "Error",
        "hanja_meaning": lines[1] if len(lines) > 1 else "",
        "explanation": lines[2] if len(lines) > 2 else response.text,
        "image_url": final_image_url
    }