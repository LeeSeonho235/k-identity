from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
import openai
import os
from dotenv import load_dotenv

# 환경 변수 로드 (Vercel 설정 혹은 .env)
load_dotenv()

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 키 설정 (직접 입력하셨다고 한 부분 유지)
# 직접 입력하셨더라도 os.getenv를 사용하면 Vercel 설정값과 연동되어 더 안전합니다.
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

gemini_client = genai.Client(api_key=GEMINI_KEY)
openai_client = openai.OpenAI(api_key=OPENAI_KEY)

# 1단계: 한국어 이름 생성
@app.get("/api/get-name")
async def get_name(english_name: str, vibe: str, gender: str, lang: str, strategy: str):
    try:
        text_prompt = (
            f"Suggest 1 Korean name for a {gender} named '{english_name}'. "
            f"Vibe: {vibe}. Strategy: {strategy}. Answer in {lang}. "
            f"Please provide your answer in exactly 3 lines:\n"
            f"Line 1: Only the Korean name (e.g., 김도윤)\n"
            f"Line 2: Hanja meaning (e.g., 道 (Path) + 潤 (Shining))\n"
            f"Line 3: A brief, warm explanation about the name."
        )
        
        response = gemini_client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=text_prompt
        )
        
        if not response.text:
            raise ValueError("Gemini returned empty response")

        lines = [line.strip() for line in response.text.strip().split('\n') if line.strip()]
        
        # 최소 3줄이 안 올 경우를 대비한 안전장치
        return {
            "korean_name": lines[0] if len(lines) > 0 else "N/A",
            "hanja_meaning": lines[1] if len(lines) > 1 else "N/A",
            "explanation": lines[2] if len(lines) > 2 else response.text
        }
    except Exception as e:
        print(f"Gemini Error: {str(e)}")
        # 프론트엔드가 에러임을 알 수 있도록 500 에러를 던집니다.
        raise HTTPException(status_code=500, detail=str(e))

# 2단계: 이미지 생성
@app.get("/api/get-image")
async def get_image(k_name: str, gender: str, vibe: str):
    try:
        dalle_prompt = (
            f"A high-quality, stylish K-pop {gender} portrait photo, "
            f"inspired by the Korean name '{k_name}'. "
            f"Overall vibe is {vibe}. Clean background, soft lighting, 4k resolution."
        )
        
        img_response = openai_client.images.generate(
            model="dall-e-3", 
            prompt=dalle_prompt, 
            n=1
        )
        
        return {"image_url": img_response.data[0].url}
    except Exception as e:
        print(f"DALL-E Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))