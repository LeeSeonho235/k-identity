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
Naming strategy: {strategy}

CRITICAL NAMING RULES:
- The name MUST sound like a real Korean person's name that Koreans actually use
- NEVER simply transliterate the foreign name phonetically (e.g. Judy→주디, Mike→마이크 is FORBIDDEN)
- Choose a name that a real Korean parent would give their child
- The name should be 2-3 syllables, feel natural in Korean

NAME TYPE - Choose ONE based on the name:
TYPE A - Hanja name (most common): Use meaningful Chinese characters
  Format: 한글이름(漢字漢字)
  Example: 민준(旻俊) or 서연(瑞妍)

TYPE B - Pure Korean name (순우리말): Use if it fits the vibe better
  No Hanja exists for these - use [PURE] marker
  Format: 한글이름[PURE]
  Example: 하늘[PURE] or 빛나[PURE]

OUTPUT FORMAT - EXACTLY 3 lines, NO labels, NO numbers:

Line 1: The Korean name with Hanja in parentheses OR [PURE] marker
Line 2: 
  - For Hanja names: Each character and its meaning in {target_lang}, format exactly: 漢 (meaning) · 字 (meaning)
  - For Pure Korean: The meaning in {target_lang}, format exactly: [PURE] meaning of the name
Line 3: Poetic explanation in 2-3 sentences in {target_lang}. Do NOT mention the foreign person's original name.

IMPORTANT FOR LINE 2:
- Use ONLY the format shown above
- Do NOT add extra words, descriptions, or alternate meanings
- Each Hanja gets exactly ONE short meaning word, not a phrase
- Maximum 2 Hanja characters shown
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
        # meaning_raw already has [PURE] prefix from prompt, clean it
        meaning_raw = meaning_raw.replace("[PURE]", "").strip()

    # ── Enforce clean meaning format ──
    # Remove any garbage that doesn't match Hanja (char) · pattern
    if not is_pure_korean:
        # Keep only pattern: X (word) · Y (word)
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


    image_url = ""
    if clean_lines:
        style_prompt_map = {
            "sound": (
                f"Portrait illustration of a modern Korean {gender}, "
                f"wearing a stylish fusion of contemporary fashion with subtle traditional Korean hanbok elements. "
                f"{vibe} expression and atmosphere. Soft watercolor background with delicate cherry blossoms. "
                f"Clean, elegant, K-pop idol aesthetic meets traditional beauty. No text. Centered portrait."
            ),
            "meaning": (
                f"Portrait illustration of a modern Korean {gender}, "
                f"wearing refined contemporary Korean fashion with traditional hanbok-inspired details. "
                f"{vibe} mood. Soft floral background with lotus and plum blossoms in pastel tones. "
                f"Sophisticated, editorial, timeless Korean beauty. No text. Centered portrait."
            ),
            "kdrama": (
                f"Portrait illustration of a modern Korean {gender} in K-drama lead role style. "
                f"Wearing elegant contemporary outfit with subtle traditional Korean aesthetic accents. "
                f"{vibe} vibe. Cinematic lighting, cherry blossom background, soft warm tones. "
                f"Think modern Korean drama lead — beautiful, charismatic, stylish. No text. Centered portrait."
            ),
        }
        dalle_prompt = style_prompt_map.get(style, style_prompt_map["kdrama"])
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