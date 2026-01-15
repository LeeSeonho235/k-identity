from fastapi.responses import FileResponse 
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google import genai 
import openai
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
# DALL-E 3 이미지 생성용 클라이언트 (유료, 5~10초 소요)
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/")
async def read_index():
    return FileResponse('index.html')

@app.get("/api/generate-k-identity")
async def generate_k_identity(english_name: str, vibe: str, gender: str, lang: str, strategy: str):
    # --- 1. Gemini로 이름과 깔끔한 3줄 요약 만들기 ---
    text_prompt = f"""
    Create 1 Korean name for {gender} named '{english_name}' using the {strategy} method with a '{vibe}' vibe.
    Answer strictly in {lang} using the format below. Do not add any extra text.
    
    Line 1: [Name in Hanja]
    Line 2: [Meaning]
    Line 3: [A short, beautiful explanation]
    """
    # 최신 gemini-2.0-flash 사용
    response = gemini_client.models.generate_content(model="gemini-2.0-flash", contents=text_prompt)
    lines = response.text.strip().split('\n')

    # --- 2. DALL-E 3로 AI 프로필 사진 그리기 ---
    dalle_prompt = f"A stylish K-pop profile photo of a {gender}, inspired by the Korean name '{lines[0]}'. Vibe: {vibe}, trendy, high quality, studio portrait."
    try:
        img_response = openai_client.images.generate(model="dall-e-3", prompt=dalle_prompt, n=1)
        image_url = img_response.data[0].url
    except Exception as e:
        print(f"DALL-E Error: {e}")
        image_url = "" # 에러 나면 빈 이미지 주소

    # --- 3. 모든 결과를 한 번에 반환  ---
    return {
        "k_name": lines[0] if len(lines) > 0 else "Error",
        "meaning": lines[1] if len(lines) > 1 else "",
        "explain": lines[2] if len(lines) > 2 else response.text,
        "image_url": image_url # 여기서 이미지가 안 오면 빈 값
    }