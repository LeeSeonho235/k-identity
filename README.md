# K-Name Generator

Korean name generator for foreigners enter your English name and get a Korean name with Hanja meanings and an AI-generated portrait card.

> Previously live at **knamegenerator.com** (now archived)

![Status](https://img.shields.io/badge/status-archived-yellow)

<img width="501" alt="Main Screen" src="https://github.com/user-attachments/assets/627a0e5c-2fb5-499b-ae9e-cd073c73305d" />
<img width="504" alt="Name Card Front" src="https://github.com/user-attachments/assets/a5b77c34-f000-4e0b-9c99-f9c30a477b74" />
<img width="226" height="321" alt="스크린샷 2026-07-04 17 06 24 복사본" src="https://github.com/user-attachments/assets/b6b78adb-d021-489f-9d0f-6498118308c2" />
<img width="217" height="319" alt="스크린샷 2026-07-04 17 06 32" src="https://github.com/user-attachments/assets/814a63c7-35f0-4768-bbeb-dd5c8bfc1e54" />




## What It Does

Users enter their English name, select gender and personality, and the app generates:

- A Korean name (한글) with Hanja (漢字) characters or pure Korean (순우리말)
- Meaning of each character explained in the user's language
- An AI-generated portrait in traditional Korean hanbok style (via DALL-E 3)
- A flippable card — front shows portrait, back shows Hanja breakdown
- Downloadable name card ($1 per download via PayPal)

Supports 5 languages: English, Spanish, Chinese, Japanese, Korean.

## Name Styles

- **Sound** — phonetically similar to the user's English name
- **Meaning** — Hanja characters matching user's personality
- **K-Drama** — inspired by K-Drama character naming patterns

## Card Styles

Users can choose from 4 visual styles for their name card:

Classic · Pastel · 4th Gen · Luxury

<img width="806" height="316" alt="스크린샷 2026-07-05 13 13 19" src="https://github.com/user-attachments/assets/9fadb253-a29d-4bc4-9f28-420928658865" />
<img width="834" height="341" alt="스크린샷 2026-07-05 13 14 33" src="https://github.com/user-attachments/assets/38671d8d-4d60-43b8-8ec1-e848dfd75eb6" />



## Tech Stack

- **Backend:** Python, FastAPI
- **Name Generation:** Google Gemini 2.0 Flash
- **Image Generation:** OpenAI DALL-E 3
- **Auth:** Supabase (Google OAuth)
- **Payment:** PortOne (PayPal)
- **Analytics:** Google Analytics, AdSense
- **Deployment:** Railway
- **Frontend:** Vanilla HTML/CSS/JS

## How It Works

```
User Input (Name, Gender, Vibe, Style, Language)
    │
    ├── Gemini 2.0 Flash → Korean Name + Hanja + Meaning
    │
    ├── DALL-E 3 → Hanbok Portrait Card (4 visual styles)
    │       └── Image Proxy (server-side, for CORS)
    │
    ├── Supabase → Google OAuth + Credit Management
    │
    └── PortOne → PayPal Payment ($1 per card download)
```

## Setup

```bash
git clone https://github.com/LeeSeonho235/k-identity.git
cd k-identity
pip install -r requirements.txt
```

Create a `.env` file:

```
GEMINI_API_KEY=your_key
OPENAI_API_KEY=your_key
SUPABASE_URL=your_url
SUPABASE_SERVICE_ROLE_KEY=your_key
SUPABASE_ANON_KEY=your_key
PORTONE_API_SECRET=your_secret
PORTONE_STORE_ID=your_store_id
PORTONE_CHANNEL_KEY_PAYPAL=your_key
```

Run:

```bash
uvicorn main:app --reload
```

## Things I Learned Building This

- Chaining multiple AI APIs (Gemini + DALL-E) in a single request pipeline
- Building a server-side image proxy to bypass CORS restrictions from DALL-E
- Regex-based post-processing to parse structured AI outputs (Hanja extraction)
- Payment flow with PortOne + PayPal for per-download purchases
- User auth and credit management with Supabase
- SEO basics: sitemap.xml, robots.txt, AdSense setup

## License

MIT
