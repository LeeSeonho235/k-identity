from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from google import genai
import openai
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

app = FastAPI()

# CORS 설정: 프론트엔드와의 통신을 허용합니다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 클라이언트 설정 (Vercel 설정에서 API 키를 넣어야 작동합니다)
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/")
async def read_index():
    # 루트 접속 시 index.html 반환
    return FileResponse('index.html')

# 1단계: 한국어 이름 생성 (Gemini 1.5 Flash 사용 - 빠름)
@app.get("/api/get-name")
async def get_name(english_name: str, vibe: str, gender: str, lang: str, strategy: str):
    try:
        # Gemini가 정확히 3줄로 답변하도록 프롬프트를 강화했습니다.
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
        
        # 응답 텍스트를 줄 단위로 나눕니다.
        lines = [line.strip() for line in response.text.strip().split('\n') if line.strip()]
        
        # 프론트엔드(index.html)에서 data.korean_name 등으로 접근하므로 키 이름을 맞춥니다.
        return {
            "korean_name": lines[0] if len(lines) > 0 else "Error",
            "hanja_meaning": lines[1] if len(lines) > 1 else "",
            "explanation": lines[2] if len(lines) > 2 else response.text
        }
    except Exception as e:
        print(f"Gemini Error: {e}")
        return {"error": str(e)}, 500

# 2단계: 이미지 생성 (DALL-E 3 사용 - 약 10초 소요)
@app.get("/api/get-image")
async def get_image(k_name: str, gender: str, vibe: str):
    try:
        # DALL-E 3를 위한 프롬프트 구성
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
        print(f"DALL-E Error: {e}")
        return {"error": str(e)}, 500