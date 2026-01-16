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
# api/main.py 수정 부분

@app.get("/api/generate-k-identity")
async def generate_k_identity(english_name: str, vibe: str, gender: str, lang: str, strategy: str):
    
    # 1. 언어 코드 매핑 (LLM의 이해도를 높이기 위해) 
    lang_map = {
        "en": "English",
        "es": "Spanish",
        "zh": "Chinese",
        "ja": "Japanese"
    }
    target_lang = lang_map.get(lang, "English")

    # 2. 프롬프트 강화: "한국어 이름"만 한국어로, 나머지는 target_lang으로! 
    text_prompt = f"""
    Role: Professional Korean Name Consultant.
    Task: Suggest 1 best Korean name for a {gender} named '{english_name}' with a '{vibe}' vibe based on {strategy}.
    
    STRICT FORMAT RULES:
    - Line 1 (Name): [Hangeul Name]([Hanja Name]) 
      * NO English, NO phonetics, NO spaces.
      * GOOD Example: 지연(智娟)
      * BAD Example: 지연(Ji-yeon)(智娟)
    
    - Line 2 (Meaning): [Meaning] ([Hanja]) 
      * Format each character clearly in {target_lang}.
      * Example: WISE (智), BEAUTIFUL (娟)
    
    - Line 3 (Description): 2-3 poetic sentences written strictly in {target_lang}.
    
    STRICT LANGUAGE RULE:
    - Only Line 1 uses Korean. 
    - Lines 2 and 3 must be written entirely in {target_lang}.
    """
    
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