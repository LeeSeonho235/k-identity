from fastapi.responses import FileResponse 
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google import genai 
import openai
from dotenv import load_dotenv
import re

load_dotenv()
app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/")
async def read_index():
    return FileResponse('index.html')

@app.get("/api/generate-k-identity")
async def generate_k_identity(english_name: str, vibe: str, gender: str, lang: str, strategy: str):
    
    lang_map = {"en": "English", "es": "Spanish", "zh": "Chinese", "ja": "Japanese"}
    target_lang = lang_map.get(lang, "English")

    # 1. 프롬프트 수정: 라벨을 아예 명시하지 않고 예시(Example)로만 지시합니다.
    text_prompt = f"""
    Role: Professional Korean Name Consultant.
    Task: Suggest 1 best Korean name for a {gender} named '{english_name}' with a '{vibe}' vibe based on {strategy}.
    
    STRICT RULES:
    - NEVER use labels like 'Line 1', 'Name:', 'Meaning:', or 'Description:'.
    - Line 1: Hangeul(Hanja) ONLY. No English, no phonetics. (Example: 지연(智娟))
    - Line 2: Hanja breakdown in {target_lang}. (Example: WISE (智), BEAUTIFUL (娟))
    - Line 3: A poetic explanation in 2-3 sentences in {target_lang}.
    
    IMPORTANT: Provide only the raw text for each line.
    """
    
    response = gemini_client.models.generate_content(model="gemini-2.0-flash", contents=text_prompt)
    
    # 2. 정규표현식 강화: 'Line 1:', 'Name:', '(Name):' 등 모든Hallucination 라벨 제거
    raw_lines = response.text.strip().split('\n')
    clean_lines = []
    for line in raw_lines:
        if line.strip():
            # 'Line 1 (Name):' 같은 복잡한 라벨도 모두 제거하는 강력한 패턴입니다.
            cleaned = re.sub(r'^.*?(Line\s*\d+|Name|Meaning|Description|Result|Explanation).*?:\s*', '', line, flags=re.IGNORECASE).strip()
            # 맨 앞의 불필요한 대괄호나 특수문자 제거
            cleaned = re.sub(r'^[\[\]\-\*\s]+', '', cleaned)
            clean_lines.append(cleaned)

    # DALL-E 3 이미지 생성 (Jiyeon 스타일 고퀄리티 유도)
    k_name_only = clean_lines[0].split('(')[0].strip() if clean_lines else "Korean Person"
    dalle_prompt = f"A high-quality, realistic studio portrait of a stylish Korean {gender}, '{vibe}' vibe, named '{k_name_only}'. K-drama aesthetic, soft lighting, 8k."
    
    image_url = ""
    try:
        img_response = openai_client.images.generate(model="dall-e-3", prompt=dalle_prompt, n=1)
        image_url = img_response.data[0].url
    except Exception as e:
        print(f"DALL-E Error: {e}")

    return {
        "k_name": clean_lines[0] if len(clean_lines) > 0 else "Error",
        "meaning": clean_lines[1] if len(clean_lines) > 1 else "",
        "explain": clean_lines[2] if len(clean_lines) > 2 else response.text,
        "image_url": image_url
    }