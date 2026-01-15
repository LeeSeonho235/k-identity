from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import openai
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 키 가져오기
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

# 제미나이 설정
genai.configure(api_key=GEMINI_KEY)

# 💡 핵심: Gemini 2.0 Flash (실험적 버전) 모델명을 정확히 입력합니다.
# 이 모델명은 현재 가장 최신이며, 404 에러를 피할 수 있는 공식 명칭입니다.
model = genai.GenerativeModel('gemini-2.0-flash-exp')

openai_client = openai.OpenAI(api_key=OPENAI_KEY)

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
        
        # 호출 방식
        response = model.generate_content(text_prompt)
        
        if not response or not response.text:
            raise ValueError("Gemini API 응답 없음")

        lines = [line.strip() for line in response.text.strip().split('\n') if line.strip()]
        
        return {
            "korean_name": lines[0] if len(lines) > 0 else "N/A",
            "hanja_meaning": lines[1] if len(lines) > 1 else "N/A",
            "explanation": lines[2] if len(lines) > 2 else response.text
        }
    except Exception as e:
        print(f"Error Details: {str(e)}")
        # 에러 발생 시 상세 내용을 브라우저에 표시하여 원인 파악을 돕습니다.
        raise HTTPException(status_code=500, detail=f"Gemini 2.0 Error: {str(e)}")

@app.get("/api/get-image")
async def get_image(k_name: str, gender: str, vibe: str):
    try:
        dalle_prompt = (
            f"A high-quality, stylish K-pop {gender} portrait photo, inspired by the Korean name '{k_name}'. Overall vibe is {vibe}. Clean background, 4k resolution."
        )
        img_response = openai_client.images.generate(model="dall-e-3", prompt=dalle_prompt, n=1)
        return {"image_url": img_response.data[0].url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))