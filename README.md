# SocialMath 🧠 — Social Pattern Decoder

A visual social skills learning app for children with autism, built with
Python/Flask and Claude AI. Everything is image-based — no text required
to navigate or play.

## Features

- 🎮 **Practice** — Claude generates visual scenes; identify emotions and pick responses
- 🔍 **Decode** — Pick observed signals in real life and get instant probability breakdowns
- 📚 **Library** — Auto-growing personal rulebook of learned social patterns
- 📊 **Stats** — Accuracy tracking, streaks, emotion-by-emotion breakdown

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/socialmath.git
cd socialmath
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set your API key
```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
```

### 5. Run
```bash
python app.py
```

Open http://localhost:5000

## Tech Stack

- **Backend**: Python + Flask
- **AI**: Anthropic Claude (`claude-sonnet-4-6`)
- **Frontend**: Vanilla HTML/CSS/JS — no build step needed
- **Storage**: localStorage (no database required)
