from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google import genai
import openai
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/api/generate-k-identity")
async def generate_k_identity(english_name: str, vibe: str, gender: str, lang: str, strategy: str):
    # 1. Gemini 2.0 모델 사용
    text_prompt = f"Suggest 1 Korean name for a {gender} named '{english_name}' with a '{vibe}' vibe based on {strategy}. Answer in {lang}. Line 1: Name(Hanja), Line 2: Meaning, Line 3: Explanation."
    response = gemini_client.models.generate_content(model="gemini-2.0-flash", contents=text_prompt)
    lines = response.text.strip().split('\n')

    # 2. DALL-E 3 이미지 생성 (Render는 타임아웃이 넉넉합니다)
    dalle_prompt = f"A stylish K-pop {gender} portrait, inspired by the name '{lines[0]}'. Vibe: {vibe}."
    img_response = openai_client.images.generate(model="dall-e-3", prompt=dalle_prompt, n=1)
    
    # 3. HTML의 변수 이름에 딱 맞춰서 반환 (변수명 일치 완료!)
    return {
        "k_name": lines[0] if len(lines) > 0 else "Error",
        "meaning": lines[1] if len(lines) > 1 else "",
        "explain": lines[2] if len(lines) > 2 else response.text,
        "image_url": img_response.data[0].url
    }