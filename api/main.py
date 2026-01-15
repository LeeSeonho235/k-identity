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
    
    # 영문 이름 포함 금지 및 3줄 포맷 강조
    text_prompt = f"""
    Suggest 1 best Korean name for a {gender} named '{english_name}' with a '{vibe}' vibe based on {strategy}.
    Answer strictly in {lang}. 
    Line 1: [Hangeul Name] ([Hanja Name]) - ONLY Korean/Hanja here.
    Line 2: [Hanja meaning]
    Line 3: [A poetic explanation]
    """
    
    response = gemini_client.models.generate_content(model="gemini-2.0-flash", contents=text_prompt)
    
    raw_lines = response.text.strip().split('\n')
    clean_lines = [re.sub(r'^(Line \d+:|Name:|Meaning:|Explanation:)', '', line).strip() for line in raw_lines if line.strip()]

    k_name_for_dalle = clean_lines[0].split('(')[0] if clean_lines else "Korean person"
    dalle_prompt = f"A high-quality studio portrait of a stylish Korean {gender}, aesthetic inspired by '{k_name_for_dalle}', {vibe} vibe, 8k."
    
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