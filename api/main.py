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

# --------------------
# 기본 설정
# --------------------
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

# --------------------
# 정적 파일
# --------------------
@app.get("/")
async def read_index():
    return FileResponse("index.html")

# --------------------
# 🔥 핵심 1: DALL·E 이미지 프록시 (Canvas 문제 해결)
# --------------------
@app.get("/api/proxy-image")
async def proxy_image(url: str):
    # OpenAI 이미지 도메인만 허용 (보안)
    if not url.startswith("https://oaidalleapiprodscus.blob.core.windows.net/"):
        raise HTTPException(status_code=400, detail="Invalid image source")

    async with httpx.AsyncClient(timeout=10) as client:
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

# --------------------
# 🔥 핵심 2: 이름 + 이미지 생성 API
# --------------------
@app.get("/api/generate-k-identity")
async def generate_k_identity(
    english_name: str,
    vibe: str,
    gender: str,
    lang: str,
    strategy: str,
):
    lang_map = {
        "en": "English",
        "es": "Spanish",
        "zh": "Chinese",
        "ja": "Japanese",
    }
    target_lang = lang_map.get(lang, "English")

    # ---------- Gemini 프롬프트 ----------
    text_prompt = f"""
Role: Professional Korean Name Consultant.

Task:
Suggest ONE best Korean name for a {gender} named "{english_name}"
with a "{vibe}" vibe based on {strategy}.

STRICT RULES:
- Output EXACTLY 3 lines
- DO NOT use labels, numbers, or prefixes

Line 1:
Korean name in Hangul with Hanja in parentheses
Example: 새롬(新美)

Line 2:
Hanja meaning in {target_lang}
Example: NEW (新), BEAUTIFUL (美)

Line 3:
Poetic explanation in 2–3 sentences in {target_lang}
"""

    response = gemini_client.models.generate_content(
        model="gemini-2.0-flash",
        contents=text_prompt,
    )

    # ---------- 응답 정제 ----------
    raw_lines = response.text.strip().split("\n")
    clean_lines = []

    for line in raw_lines:
        if not line.strip():
            continue
        cleaned = re.sub(
            r'^.*?(Line\s*\d+|Name|Meaning|Description|Explanation).*?:\s*',
            '',
            line,
            flags=re.IGNORECASE,
        ).strip()
        cleaned = re.sub(r'^[\[\]\-\*\s]+', '', cleaned)
        clean_lines.append(cleaned)

    # ---------- DALL·E 3 이미지 ----------
    image_url = ""
    if clean_lines:
        k_name_only = clean_lines[0].split("(")[0].strip()
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

            # ⭐️ 핵심: 프록시 URL로 변환
            image_url = f"/api/proxy-image?url={quote(raw_url)}"

        except Exception as e:
            print("DALL·E Error:", e)

    return {
        "k_name": clean_lines[0] if len(clean_lines) > 0 else "Error",
        "meaning": clean_lines[1] if len(clean_lines) > 1 else "",
        "explain": clean_lines[2] if len(clean_lines) > 2 else "",
        "image_url": image_url,
    }
