from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai # 안정적인 라이브러리로 변경
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

# API 키 설정
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

# 제미나이 설정 (기존 안정 방식)
genai.configure(api_key=GEMINI_KEY)
# 모델 선언 (버전 명시를 피하고 표준 명칭 사용)
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

openai_client = openai.OpenAI(api_key=OPENAI_KEY)

# 1단계: 이름 생성 API
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
        
        # 호출 방식 변경
        response = gemini_model.generate_content(text_prompt)
        
        if not response.text:
            raise ValueError("Gemini response is empty")

        lines = [line.strip() for line in response.text.strip().split('\n') if line.strip()]
        
        return {
            "korean_name": lines[0] if len(lines) > 0 else "N/A",
            "hanja_meaning": lines[1] if len(lines) > 1 else "N/A",
            "explanation": lines[2] if len(lines) > 2 else response.text
        }
    except Exception as e:
        print(f"Gemini Error Trace: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Gemini Error: {str(e)}")

# 2단계: 이미지 생성 API
@app.get("/api/get-image")
async def get_image(k_name: str, gender: str, vibe: str):
    try:
        dalle_prompt = (
            f"A high-quality, stylish K-pop {gender} portrait photo, "
            f"inspired by the Korean name '{k_name}'. "
            f"Overall vibe is {vibe}. Clean background, soft lighting, 4k resolution."
        )
        img_response = openai_client.images.generate(model="dall-e-3", prompt=dalle_prompt, n=1)
        return {"image_url": img_response.data[0].url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))