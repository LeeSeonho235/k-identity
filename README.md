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

<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { 
    background: #0d1117; 
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 40px 20px;
    gap: 60px;
  }

  h2 {
    color: #e6edf3;
    font-size: 18px;
    font-weight: 500;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 10px;
  }

  .row {
    display: flex;
    gap: 24px;
    justify-content: center;
    flex-wrap: wrap;
  }

  .card-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
  }

  .style-label {
    color: #8b949e;
    font-size: 13px;
    letter-spacing: 3px;
    text-transform: uppercase;
    font-weight: 600;
  }

  .card {
    width: 220px;
    height: 320px;
    border-radius: 16px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
  }

  /* ===== BACK CARDS (Hanja side) ===== */

  /* Classic */
  .classic-back {
    background: #1a1d2e;
    border: 2px solid #c8a84e;
  }
  .classic-back .top-label { color: #c8a84e; }
  .classic-back .eng-name { color: #c8a84e; }
  .classic-back .kor-name { color: #ffffff; }
  .classic-back .hanja-char { color: #c8a84e; }
  .classic-back .hanja-meaning { color: #c8a84e; }
  .classic-back .divider { background: #c8a84e; }
  .classic-back .dot { border-color: #c8a84e; }
  .classic-back .bottom-info { color: #8b8b8b; }

  /* Pastel */
  .pastel-back {
    background: #fce4ec;
    border: 2px solid #f8bbd0;
  }
  .pastel-back .top-label { color: #e91e63; }
  .pastel-back .eng-name { color: #e91e63; }
  .pastel-back .kor-name { color: #880e4f; }
  .pastel-back .hanja-char { color: #e91e63; }
  .pastel-back .hanja-meaning { color: #ad1457; }
  .pastel-back .divider { background: #f48fb1; }
  .pastel-back .dot { border-color: #f48fb1; }
  .pastel-back .bottom-info { color: #c2185b; }

  /* 4th Gen */
  .gen4-back {
    background: #0a0a0a;
    border: 2px solid #00e5ff;
    box-shadow: 0 0 15px rgba(0, 229, 255, 0.2);
  }
  .gen4-back .top-label { color: #00e5ff; }
  .gen4-back .eng-name { color: #00e5ff; }
  .gen4-back .kor-name { color: #ffffff; }
  .gen4-back .hanja-char { color: #00e5ff; text-shadow: 0 0 10px rgba(0, 229, 255, 0.5); }
  .gen4-back .hanja-meaning { color: #00e5ff; }
  .gen4-back .divider { background: #00e5ff; }
  .gen4-back .dot { border-color: #00e5ff; }
  .gen4-back .bottom-info { color: #546e7a; }

  /* Luxury */
  .luxury-back {
    background: #1a0a2e;
    border: 2px solid #b388ff;
  }
  .luxury-back .top-label { color: #ce93d8; }
  .luxury-back .eng-name { color: #ce93d8; }
  .luxury-back .kor-name { color: #e1bee7; }
  .luxury-back .hanja-char { color: #ce93d8; }
  .luxury-back .hanja-meaning { color: #ba68c8; }
  .luxury-back .divider { background: #9c27b0; }
  .luxury-back .dot { border-color: #9c27b0; }
  .luxury-back .bottom-info { color: #7b1fa2; }

  /* ===== FRONT CARDS (Portrait side) ===== */

  .classic-front {
    background: #1a1d2e;
    border: 2px solid #c8a84e;
  }
  .classic-front .portrait-ring { border-color: #c8a84e; }
  .classic-front .front-name { color: #ffffff; }
  .classic-front .front-meaning { color: #c8a84e; }
  .classic-front .front-label { color: #c8a84e; }

  .pastel-front {
    background: #fce4ec;
    border: 2px solid #f8bbd0;
  }
  .pastel-front .portrait-ring { border-color: #f48fb1; }
  .pastel-front .front-name { color: #880e4f; }
  .pastel-front .front-meaning { color: #e91e63; }
  .pastel-front .front-label { color: #e91e63; }

  .gen4-front {
    background: #0a0a0a;
    border: 2px solid #00e5ff;
    box-shadow: 0 0 15px rgba(0, 229, 255, 0.2);
  }
  .gen4-front .portrait-ring { border-color: #00e5ff; box-shadow: 0 0 10px rgba(0, 229, 255, 0.3); }
  .gen4-front .front-name { color: #ffffff; }
  .gen4-front .front-meaning { color: #00e5ff; }
  .gen4-front .front-label { color: #00e5ff; }

  .luxury-front {
    background: #1a0a2e;
    border: 2px solid #b388ff;
  }
  .luxury-front .portrait-ring { border-color: #b388ff; }
  .luxury-front .front-name { color: #e1bee7; }
  .luxury-front .front-meaning { color: #ce93d8; }
  .luxury-front .front-label { color: #ce93d8; }

  /* ===== Shared card elements ===== */
  .top-label {
    font-size: 11px;
    letter-spacing: 4px;
    font-weight: 700;
    position: absolute;
    top: 16px;
  }
  .eng-name {
    font-size: 20px;
    letter-spacing: 8px;
    font-weight: 600;
    margin-top: 10px;
  }
  .divider-line {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 12px 0;
    width: 70%;
  }
  .divider {
    flex: 1;
    height: 1px;
  }
  .dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    border: 1px solid;
  }
  .kor-name {
    font-size: 56px;
    font-weight: 700;
    letter-spacing: 12px;
  }
  .hanja-row {
    display: flex;
    gap: 40px;
    margin-top: 8px;
  }
  .hanja-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
  }
  .hanja-char {
    font-size: 32px;
    font-weight: 600;
  }
  .hanja-sep {
    width: 1px;
    height: 30px;
    opacity: 0.3;
  }
  .hanja-meaning {
    font-size: 10px;
    letter-spacing: 2px;
    font-weight: 600;
  }
  .bottom-info {
    position: absolute;
    bottom: 12px;
    font-size: 9px;
    letter-spacing: 1px;
  }

  /* Front card elements */
  .front-label {
    font-size: 11px;
    letter-spacing: 4px;
    font-weight: 700;
    position: absolute;
    top: 16px;
  }
  .portrait-ring {
    width: 110px;
    height: 110px;
    border-radius: 50%;
    border: 2px solid;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 20px;
    overflow: hidden;
    background: rgba(255,255,255,0.05);
  }
  .portrait-placeholder {
    font-size: 48px;
  }
  .front-bottom {
    position: absolute;
    bottom: 0;
    width: 100%;
    padding: 20px;
    text-align: center;
    background: rgba(0,0,0,0.7);
    border-radius: 0 0 14px 14px;
  }
  .pastel-front .front-bottom {
    background: rgba(136, 14, 79, 0.1);
  }
  .front-name {
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 4px;
  }
  .front-meaning {
    font-size: 11px;
    letter-spacing: 2px;
    font-weight: 500;
  }

  .section-label {
    color: #8b949e;
    font-size: 12px;
    letter-spacing: 1px;
    margin-bottom: 4px;
  }
</style>
</head>
<body>

<!-- Back cards (Hanja side) -->
<div>
  <div class="row">
    <!-- Classic Back -->
    <div class="card-wrapper">
      <span class="style-label" style="color:#c8a84e;">✦ CLASSIC</span>
      <div class="card classic-back">
        <span class="top-label">K · N A M E</span>
        <span class="eng-name">J U L Y</span>
        <div class="divider-line">
          <div class="divider"></div>
          <div class="dot"></div>
          <div class="divider"></div>
        </div>
        <span class="kor-name">주 아</span>
        <div class="divider-line">
          <div class="divider"></div>
          <div class="dot"></div>
          <div class="divider"></div>
        </div>
        <div class="hanja-row">
          <div class="hanja-item">
            <span class="hanja-char">珠</span>
            <span class="hanja-meaning">PEARL</span>
          </div>
          <div class="hanja-item">
            <span class="hanja-char">雅</span>
            <span class="hanja-meaning">ELEGANT</span>
          </div>
        </div>
        <span class="bottom-info">july · female · Cool</span>
      </div>
    </div>

    <!-- Pastel Back -->
    <div class="card-wrapper">
      <span class="style-label" style="color:#f48fb1;">✿ PASTEL</span>
      <div class="card pastel-back">
        <span class="top-label">K · N A M E</span>
        <span class="eng-name">J U L Y</span>
        <div class="divider-line">
          <div class="divider"></div>
          <div class="dot"></div>
          <div class="divider"></div>
        </div>
        <span class="kor-name">주 아</span>
        <div class="divider-line">
          <div class="divider"></div>
          <div class="dot"></div>
          <div class="divider"></div>
        </div>
        <div class="hanja-row">
          <div class="hanja-item">
            <span class="hanja-char">珠</span>
            <span class="hanja-meaning">PEARL</span>
          </div>
          <div class="hanja-item">
            <span class="hanja-char">雅</span>
            <span class="hanja-meaning">ELEGANT</span>
          </div>
        </div>
        <span class="bottom-info">july · female · Cool</span>
      </div>
    </div>

    <!-- 4th Gen Back -->
    <div class="card-wrapper">
      <span class="style-label" style="color:#00e5ff;">⚡ 4TH GEN</span>
      <div class="card gen4-back">
        <span class="top-label">K · N A M E</span>
        <span class="eng-name">J U L Y</span>
        <div class="divider-line">
          <div class="divider"></div>
          <div class="dot"></div>
          <div class="divider"></div>
        </div>
        <span class="kor-name">주 아</span>
        <div class="divider-line">
          <div class="divider"></div>
          <div class="dot"></div>
          <div class="divider"></div>
        </div>
        <div class="hanja-row">
          <div class="hanja-item">
            <span class="hanja-char">珠</span>
            <span class="hanja-meaning">PEARL</span>
          </div>
          <div class="hanja-item">
            <span class="hanja-char">雅</span>
            <span class="hanja-meaning">ELEGANT</span>
          </div>
        </div>
        <span class="bottom-info">july · female · Cool</span>
      </div>
    </div>

    <!-- Luxury Back -->
    <div class="card-wrapper">
      <span class="style-label" style="color:#ce93d8;">♥ LUXURY</span>
      <div class="card luxury-back">
        <span class="top-label">✦ K · N A M E ✦</span>
        <span class="eng-name">J U L Y</span>
        <div class="divider-line">
          <div class="divider"></div>
          <div class="dot"></div>
          <div class="divider"></div>
        </div>
        <span class="kor-name">주 아</span>
        <div class="divider-line">
          <div class="divider"></div>
          <div class="dot"></div>
          <div class="divider"></div>
        </div>
        <div class="hanja-row">
          <div class="hanja-item">
            <span class="hanja-char">珠</span>
            <span class="hanja-meaning">PEARL</span>
          </div>
          <div class="hanja-item">
            <span class="hanja-char">雅</span>
            <span class="hanja-meaning">ELEGANT</span>
          </div>
        </div>
        <span class="bottom-info">july · female · Cool</span>
      </div>
    </div>
  </div>
</div>

<!-- Front cards (Portrait side) -->
<div>
  <div class="row">
    <!-- Classic Front -->
    <div class="card-wrapper">
      <span class="style-label" style="color:#8b949e;">FRONT</span>
      <div class="card classic-front">
        <span class="front-label">K · N A M E</span>
        <div class="portrait-ring">
          <span class="portrait-placeholder">👩</span>
        </div>
        <div class="front-bottom">
          <div class="front-name">주아(珠雅)</div>
          <div class="front-meaning">珠 (PEARL) · 雅 (ELEGANT)</div>
        </div>
      </div>
    </div>

    <!-- Pastel Front -->
    <div class="card-wrapper">
      <span class="style-label" style="color:#8b949e;">FRONT</span>
      <div class="card pastel-front">
        <span class="front-label">✦ K · N A M E ✦</span>
        <div class="portrait-ring">
          <span class="portrait-placeholder">👩</span>
        </div>
        <div class="front-bottom">
          <div class="front-name">주아(珠雅)</div>
          <div class="front-meaning">珠 (PEARL) · 雅 (ELEGANT)</div>
        </div>
      </div>
    </div>

    <!-- 4th Gen Front -->
    <div class="card-wrapper">
      <span class="style-label" style="color:#8b949e;">FRONT</span>
      <div class="card gen4-front">
        <span class="front-label">K · N A M E</span>
        <div class="portrait-ring">
          <span class="portrait-placeholder">👩</span>
        </div>
        <div class="front-bottom">
          <div class="front-name">주아(珠雅)</div>
          <div class="front-meaning">珠 (PEARL) · 雅 (ELEGANT)</div>
        </div>
      </div>
    </div>

    <!-- Luxury Front -->
    <div class="card-wrapper">
      <span class="style-label" style="color:#8b949e;">FRONT</span>
      <div class="card luxury-front">
        <span class="front-label">✦ K · N A M E ✦</span>
        <div class="portrait-ring">
          <span class="portrait-placeholder">👩</span>
        </div>
        <div class="front-bottom">
          <div class="front-name">주아(珠雅)</div>
          <div class="front-meaning">珠 (PEARL) · 雅 (ELEGANT)</div>
        </div>
      </div>
    </div>
  </div>
</div>

</body>
</html>



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
