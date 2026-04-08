import os
import re
import httpx
from datetime import datetime, timedelta
from urllib.parse import quote

from fastapi import FastAPI, Response, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse
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

# ---------- Supabase ----------
try:
    from supabase import create_client
    _sb_url = os.getenv("SUPABASE_URL")
    _sb_srk = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase_admin = create_client(_sb_url, _sb_srk) if (_sb_url and _sb_srk) else None
except Exception as e:
    print(f"Supabase init error: {e}")
    supabase_admin = None

PORTONE_API_SECRET = os.getenv("PORTONE_API_SECRET", "")


# ---------- Pages ----------

@app.get("/")
async def index():
    return FileResponse("index.html")

@app.get("/pricing")
async def pricing():
    return FileResponse("pricing.html")


# ---------- SEO ----------

@app.get("/sitemap.xml")
async def sitemap():
    content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://www.knamegenerator.com/</loc>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://www.knamegenerator.com/pricing</loc>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>'''
    return Response(content=content, media_type="application/xml")

@app.get("/robots.txt")
async def robots():
    content = """User-agent: *
Allow: /
Sitemap: https://www.knamegenerator.com/sitemap.xml"""
    return Response(content=content, media_type="text/plain")

@app.get("/ads.txt")
async def ads_txt():
    content = "google.com, pub-4002075177790525, DIRECT, f08c47fec0942fa0"
    return Response(content=content, media_type="text/plain")


# ---------- Config API (환경변수를 프론트로 전달) ----------

@app.get("/api/config")
async def get_config():
    return {
        "SUPABASE_URL": os.getenv("SUPABASE_URL", ""),
        "SUPABASE_ANON_KEY": os.getenv("SUPABASE_ANON_KEY", ""),
        "PORTONE_STORE_ID": os.getenv("PORTONE_STORE_ID", ""),
        "PORTONE_CHANNEL_KEY_KAKAO": os.getenv("PORTONE_CHANNEL_KEY_KAKAO", ""),
        "PORTONE_CHANNEL_KEY_PAYPAL": os.getenv("PORTONE_CHANNEL_KEY_PAYPAL", ""),
    }


# ---------- Payment callback ----------

@app.get("/success")
async def payment_success(
    plan: str = "",
    paymentId: str = "",
    email: str = "",
):
    if not paymentId:
        return RedirectResponse("/?fail=1")

    async with httpx.AsyncClient(timeout=10) as client:
        res = await client.get(
            f"https://api.portone.io/payments/{paymentId}",
            headers={"Authorization": f"PortOne {PORTONE_API_SECRET}"},
        )
    payment = res.json()

    if payment.get("status") != "PAID":
        return RedirectResponse("/?fail=1")

    user_email = payment.get("customer", {}).get("email") or email

    expiry_map = {
        "week": timedelta(weeks=1),
        "month": timedelta(days=30),
        "annual": timedelta(days=365),
    }
    expires_at = datetime.utcnow() + expiry_map.get(plan, timedelta(days=365))

    if supabase_admin and user_email:
        supabase_admin.table("user_plans").upsert(
            {
                "email": user_email,
                "plan_type": plan,
                "plan_expires_at": expires_at.isoformat(),
            },
            on_conflict="email",
        ).execute()

    return RedirectResponse(f"/?success=1&plan={plan}")


# ---------- API: plan check ----------

@app.get("/api/my-plan")
async def my_plan(email: str):
    if not email or not supabase_admin:
        return {"plan": None}

    result = (
        supabase_admin.table("user_plans")
        .select("*")
        .eq("email", email)
        .execute()
    )
    if result.data:
        plan = result.data[0]
        expires_str = plan["plan_expires_at"]
        expires_at = datetime.fromisoformat(expires_str.replace("Z", "+00:00"))
        now = datetime.now(expires_at.tzinfo)
        if expires_at > now:
            return {"plan": plan["plan_type"], "expires_at": expires_str}
    return {"plan": None}


# ---------- API: DALL-E image proxy ----------

@app.get("/api/proxy-image")
async def proxy_image(url: str):
    if not url.startswith("https://oaidalleapiprodscus.blob.core.windows.net/"):
        raise HTTPException(status_code=400, detail="Invalid image source")

    async with httpx.AsyncClient(timeout=15) as client:
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


# ---------- API: name + image generation ----------

@app.get("/api/generate-k-identity")
async def generate_k_identity(
    english_name: str,
    vibe: str,
    gender: str,
    lang: str,
    strategy: str,
    style: str = "kdrama",
):
    lang_map = {
        "en": "English",
        "es": "Spanish",
        "zh": "Chinese",
        "ja": "Japanese",
        "ko": "Korean",
    }
    target_lang = lang_map.get(lang, "English")

    text_prompt = f"""
You are a professional Korean name consultant helping foreigners get a beautiful, authentic Korean name.

Task: Suggest ONE Korean name for a {gender} named "{english_name}" with a "{vibe}" vibe.

CRITICAL NAMING RULES:
- The name MUST sound like a real Korean person's name that Koreans actually use today
- NEVER phonetically transliterate: Judy→주디, Mike→마이크, Sally→샐리 are ALL FORBIDDEN
- Choose a name a real Korean parent would proudly give their child
- 2-3 syllables, naturally Korean-sounding

NAME TYPE - choose whichever fits better:
TYPE A - Hanja name: 민준(旻俊) or 서연(瑞妍)
TYPE B - Pure Korean (순우리말): 하늘[PURE] or 빛나[PURE]

OUTPUT FORMAT - EXACTLY 3 lines, NO labels, NO numbers, NO extra text:
Line 1: Korean name with Hanja OR [PURE] marker
Line 2: For Hanja → 漢 (meaning) · 字 (meaning) | For Pure → [PURE] one-line meaning
Line 3: Poetic 2-3 sentence description in {target_lang}. Do NOT mention their original name.

LINE 2 RULES: ONE short word per Hanja, max 2 characters, no phrases.
"""

    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=text_prompt,
        )
        raw_lines = [l for l in response.text.strip().split("\n") if l.strip()]
        clean_lines = []
        for line in raw_lines:
            cleaned = re.sub(
                r"^.*?(Line\s*\d+|Name|Meaning|Description|Explanation|TYPE\s*[AB]).*?:\s*",
                "",
                line,
                flags=re.IGNORECASE,
            ).strip()
            cleaned = re.sub(r"^[\[\]\-\*\s]+", "", cleaned)
            if cleaned:
                clean_lines.append(cleaned)
    except Exception as e:
        print(f"Gemini Error: {e}")
        clean_lines = ["민준(旻俊)", "旻 (Sky) · 俊 (Talented)", "Please try again later."]

    # ── Post-process: detect pure Korean name ──
    is_pure_korean = False
    k_name_raw = clean_lines[0] if clean_lines else ""
    meaning_raw = clean_lines[1] if len(clean_lines) > 1 else ""

    if "[PURE]" in k_name_raw:
        is_pure_korean = True
        k_name_raw = k_name_raw.replace("[PURE]", "").strip()
        meaning_raw = meaning_raw.replace("[PURE]", "").strip()

    if not is_pure_korean:
        hanja_pattern = re.compile(
            r'([\u4e00-\u9fff])\s*[（(]([^)）·\n]{1,20})[)）]\s*·?\s*'
            r'([\u4e00-\u9fff])?\s*[（(]?([^)）·\n]{0,20})[)）]?'
        )
        m = hanja_pattern.search(meaning_raw)
        if m:
            h1, m1 = m.group(1), m.group(2).strip()
            h2, m2 = m.group(3), m.group(4).strip() if m.group(4) else ""
            if h2 and m2:
                meaning_raw = f"{h1} ({m1}) · {h2} ({m2})"
            else:
                meaning_raw = f"{h1} ({m1})"

    # ── Single unified DALL-E prompt - always Korean/East Asian ──
    image_url = ""
    if clean_lines:
        dalle_prompt = (
            f"Watercolor illustration portrait of a Korean {gender}. "
            f"CRITICAL: The subject MUST have East Asian features — Korean facial structure, "
            f"monolid or natural double eyelid eyes, straight dark hair, fair smooth skin. "
            f"Style: elegant Korean beauty, similar to Korean webtoon or manhwa illustration. "
            f"Wearing traditional Korean hanbok with soft floral patterns. "
            f"Background: soft pastel watercolor with cherry blossoms and gentle ink wash. "
            f"Mood: {vibe}. Centered portrait composition. NO text in image. "
            f"The portrait must look unmistakably Korean, like a character from a Korean historical drama."
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
            print(f"DALL-E Error: {e}")
            image_url = ""

    return {
        "k_name": k_name_raw,
        "meaning": meaning_raw,
        "explain": clean_lines[2] if len(clean_lines) > 2 else "",
        "image_url": image_url,
        "is_pure": is_pure_korean,
    }