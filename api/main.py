from fastapi.responses import FileResponse 
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google import genai 
import openai
from dotenv import load_dotenv
import re  # 꼬리표 제거를 위한 정규표현식

load_dotenv()
app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/")
async def read_index():
    return FileResponse('index.html')

# 프론트엔드 fetch 주소와 일치하도록 /api/ 를 꼭 붙여야 합니다.
@app.get("/api/generate-k-identity")
async def generate_k_identity(english_name: str, vibe: str, gender: str, lang: str, strategy: str):
    
    # --- 1. Gemini 프롬프트: "지혜" 스타일로 상세 요청 ---
    # prompt 부분을 아래와 같이 수정하세요.
    text_prompt = (
    f"You are a Korean naming expert. Suggest 1 Korean name for a {gender} named '{english_name}'. "
    f"Vibe: {vibe}. Strategy: {strategy}. "
    f"IMPORTANT: You must write the 'Hanja meaning' and 'Explanation' ONLY in the language code: {lang}. " # 언어 지시 강화
    f"Provide the answer in exactly 3 lines:\n"
    f"Line 1: Only the Korean name (e.g., 김도윤)\n"
    f"Line 2: Hanja meaning in {lang}\n"
    f"Line 3: Warm explanation in {lang}"
)
    
    response = gemini_client.models.generate_content(model="gemini-2.0-flash", contents=text_prompt)
    
    # AI가 혹시라도 붙였을지 모를 "Line 1:", "Name:" 등의 꼬리표를 제거하는 로직
    raw_lines = response.text.strip().split('\n')
    clean_lines = [re.sub(r'^(Line \d+:|Name:|Meaning:|Explanation:|\[|\])', '', line).strip() for line in raw_lines if line.strip()]

    # --- 2. DALL-E 3 이미지 생성 (프롬프트 보강) ---
    # 이름과 분위기를 조합해 더 고퀄리티 사진을 유도합니다.
    k_name_only = clean_lines[0].split('(')[0].strip() if clean_lines else "Korean Person"
    dalle_prompt = f"A realistic, high-quality studio portrait of a stylish Korean {gender}, '{vibe}' vibe, inspired by the name '{k_name_only}'. K-drama aesthetic, soft lighting, 8k resolution."
    
    try:
        # Render 타임아웃 30초 내에 처리되도록 호출
        img_response = openai_client.images.generate(model="dall-e-3", prompt=dalle_prompt, n=1)
        image_url = img_response.data[0].url
    except Exception as e:
        print(f"DALL-E Error: {e}")
        image_url = "" 

    return {
        "k_name": clean_lines[0] if len(clean_lines) > 0 else "Error",
        "meaning": clean_lines[1] if len(clean_lines) > 1 else "",
        "explain": clean_lines[2] if len(clean_lines) > 2 else response.text,
        "image_url": image_url
    }