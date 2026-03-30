import os
import re
import httpx
from urllib.parse import quote

from fastapi import FastAPI, Response, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
from google import genai
import openai

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/")
async def read_index():
    return FileResponse("index.html")

@app.get("/api/proxy-image")
async def proxy_image(url: str):
    # OpenAI 이미지 도메인 보안 체크
    if not url.startswith("https://oaidalleapiprodscus.blob.core.windows.net/"):
        raise HTTPException(status_code=400, detail="Invalid image source")

    async with httpx.AsyncClient(timeout=15) as client: # 타임아웃 약간 증가
        try:
            res = await client.get(url)
            if res.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to fetch image")
            return Response(
                content=res.content,
                media_type="image/png",
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Cache-Control": "public, max-age=86400",
                },
            )
        except Exception:
            raise HTTPException(status_code=500, detail="Proxy Error")

@app.get("/api/generate-k-identity")
async def generate_k_identity(
    english_name: str,
    vibe: str,
    gender: str,
    lang: str,
    strategy: str,
):
    lang_map = {"en": "English", "es": "Spanish", "zh": "Chinese", "ja": "Japanese"}
    target_lang = lang_map.get(lang, "English")

    # 1. Gemini 이름 생성
    text_prompt = f"""
Role: Professional Korean Name Consultant.
Task: Suggest ONE best Korean name for a {gender} named "{english_name}" with a "{vibe}" vibe based on {strategy}.
STRICT RULES:
- Output EXACTLY 3 lines
- Line 1: Korean name in Hangul with Hanja in parentheses (e.g., 새롬(新美))
- Line 2: Hanja meaning in {target_lang}
- Line 3: Poetic explanation in 2-3 sentences in {target_lang}
"""
    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=text_prompt,
        )
        raw_lines = response.text.strip().split("\n")
        clean_lines = []
        for line in raw_lines:
            if not line.strip(): continue
            cleaned = re.sub(r'^.*?(Line\s*\d+|Name|Meaning|Description|Explanation).*?:\s*', '', line, flags=re.IGNORECASE).strip()
            cleaned = re.sub(r'^[\[\]\-\*\s]+', '', cleaned)
            clean_lines.append(cleaned)
    except Exception as e:
        print(f"Gemini Error: {e}")
        clean_lines = ["오류(Error)", "Service unavailable", "Please try again later."]

    # 2. DALL·E 이미지 생성 (예외 처리 강화)
    image_url = ""
    if clean_lines:
        dalle_prompt = (
            f"A high-quality, realistic studio portrait of a stylish Korean {gender}. "
            f"{vibe} vibe. K-drama aesthetic, soft lighting, ultra-detailed, 8k."
        )
        try:
            img_response = openai_client.images.generate(
                model="dall-e-3",
                prompt=dalle_prompt,
                n=1,
            )
            raw_url = img_response.data[0].url
            image_url = f"/api/proxy-image?url={quote(raw_url)}"
        except Exception as e:
            print(f"DALL·E Error: {e}")
            image_url = "" # 실패 시 빈 값 전달하여 클라이언트가 Placeholder를 쓰게 함

    return {
        "k_name": clean_lines[0] if len(clean_lines) > 0 else "Error",
        "meaning": clean_lines[1] if len(clean_lines) > 1 else "",
        "explain": clean_lines[2] if len(clean_lines) > 2 else "",
        "image_url": image_url,
    }