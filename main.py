import os
import re
import httpx
from datetime import datetime, timedelta
from urllib.parse import quote

from fastapi import FastAPI, Response, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from dotenv import load_dotenv
from google import genai
import openai

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory=".")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------- Supabase Admin ----------
try:
    from supabase import create_client
    _sb_url = os.getenv("SUPABASE_URL")
    _sb_srk = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase_admin = create_client(_sb_url, _sb_srk) if (_sb_url and _sb_srk) else None
except Exception as e:
    print(f"Supabase init error: {e}")
    supabase_admin = None

PORTONE_API_SECRET = os.getenv("PORTONE_API_SECRET", "")


def tpl(request: Request, **kwargs):
    return {
        "request": request,
        "SUPABASE_URL": os.getenv("SUPABASE_URL", ""),
        "SUPABASE_ANON_KEY": os.getenv("SUPABASE_ANON_KEY", ""),
        "PORTONE_STORE_ID": os.getenv("PORTONE_STORE_ID", ""),
        "PORTONE_CHANNEL_KEY_KAKAO": os.getenv("PORTONE_CHANNEL_KEY_KAKAO", ""),
        "PORTONE_CHANNEL_KEY_PAYPAL": os.getenv("PORTONE_CHANNEL_KEY_PAYPAL", ""),
        **kwargs,
    }


# ---------- Pages ----------

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", tpl(request))


@app.get("/pricing")
async def pricing(request: Request):
    return templates.TemplateResponse("pricing.html", tpl(request))


# ---------- Payment callback ----------

@app.get("/success")
async def payment_success(
    request: Request,
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
Role: Professional Korean Name Consultant.

Task:
Suggest ONE best Korean name for a {gender} named "{english_name}"
with a "{vibe}" vibe based on {strategy}.

STRICT RULES:
- Output EXACTLY 3 lines
- DO NOT use labels, numbers, or prefixes

Line 1: Korean name in Hangul with Hanja in parentheses
Example: 새롬(新美)

Line 2: Hanja meaning in {target_lang}
Example: NEW (新), BEAUTIFUL (美)

Line 3: Poetic explanation in 2-3 sentences in {target_lang}
"""

    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=text_prompt,
        )
        raw_lines = response.text.strip().split("\n")
        clean_lines = []
        for line in raw_lines:
            if not line.strip():
                continue
            cleaned = re.sub(
                r"^.*?(Line\s*\d+|Name|Meaning|Description|Explanation).*?:\s*",
                "",
                line,
                flags=re.IGNORECASE,
            ).strip()
            cleaned = re.sub(r"^[\[\]\-\*\s]+", "", cleaned)
            clean_lines.append(cleaned)
    except Exception as e:
        print(f"Gemini Error: {e}")
        clean_lines = ["오류(Error)", "Service unavailable", "Please try again later."]

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
            print(f"DALL-E Error: {e}")
            image_url = ""

    return {
        "k_name": clean_lines[0] if len(clean_lines) > 0 else "Error",
        "meaning": clean_lines[1] if len(clean_lines) > 1 else "",
        "explain": clean_lines[2] if len(clean_lines) > 2 else "",
        "image_url": image_url,
    }