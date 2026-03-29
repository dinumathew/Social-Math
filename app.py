import os
import json
from flask import Flask, render_template, request, jsonify
import anthropic

app = Flask(__name__)
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """You are SocialMath — a social pattern tutor for an 11-year-old autistic boy who is a
mathematics prodigy with powerful visual/image-based reasoning. He sees the world through
numbers, probabilities and patterns.

RULES:
- NEVER say "wrong." Always use percentage scores.
- Probabilities must sum to exactly 100.
- Use cause→effect logic only. No vague emotional language.
- Respond ONLY in valid JSON. No preamble, no markdown fences."""


def parse_json(text):
    t = text.strip()
    if t.startswith("```"):
        lines = t.split("\n")
        t = "\n".join(lines[1:-1])
    return json.loads(t)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/generate-scenario", methods=["POST"])
def generate_scenario():
    difficulty = request.json.get("difficulty", "medium")

    prompt = f"""Generate a social scenario. Difficulty: {difficulty}.

Return ONLY this JSON:
{{
  "id": "scn_XXXX",
  "scene": "classroom",
  "character": "classmate",
  "character_age": "child",
  "signals": ["looking_down", "crossed_arms", "quiet"],
  "true_emotion": "sad",
  "emotion_options": [
    {{"emotion": "sad",    "probability": 60, "emoji": "😢"}},
    {{"emotion": "angry",  "probability": 20, "emoji": "😠"}},
    {{"emotion": "tired",  "probability": 12, "emoji": "😴"}},
    {{"emotion": "worried","probability":  8, "emoji": "😟"}}
  ],
  "response_options": [
    {{"id":"r1","action":"Ask quietly: Are you okay?",  "icon":"💬","visual":"talk",  "score":88}},
    {{"id":"r2","action":"Give them space and wait",     "icon":"⏳","visual":"wait",  "score":72}},
    {{"id":"r3","action":"Tell a joke to cheer them up","icon":"😄","visual":"joke",  "score":40}},
    {{"id":"r4","action":"Ignore and keep working",      "icon":"📚","visual":"ignore","score":22}}
  ],
  "best_response_id": "r1",
  "pattern_rule": "looking_down + crossed_arms + quiet → sad (60%)"
}}

Rules:
- scene ∈ {{classroom, playground, home, lunchroom, hallway}}
- character ∈ {{classmate, friend, teacher, sibling, parent}}
- character_age ∈ {{child, adult}}
- signals: 2-4 items from: looking_down, crossed_arms, quiet, loud_voice, fast_speech,
  slow_speech, no_eye_contact, eye_contact, smiling, frowning, tense_posture,
  relaxed_posture, crying, laughing, fidgeting, waving, turning_away, leaning_in
- emotion_options: exactly 4, sum=100
- response_options: exactly 4; visual ∈ {{talk,wait,joke,ignore,help,wave,share,observe}}
- difficulty "{difficulty}": easy=2 strong obvious signals, medium=3 mixed, hard=4 subtle/conflicting
- Vary emotions freely: sad, happy, excited, angry, worried, confused, tired, scared"""

    msg = client.messages.create(
        model=MODEL, max_tokens=900,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )
    return jsonify(parse_json(msg.content[0].text))


@app.route("/api/evaluate", methods=["POST"])
def evaluate():
    d = request.json
    sc = d["scenario"]
    chosen_emo = d["chosen_emotion"]
    chosen_res = d["chosen_response_id"]

    true_emo = sc["true_emotion"]
    emo_opts = sc["emotion_options"]
    res_opts = sc["response_options"]

    if chosen_emo == true_emo:
        emo_score = 100
    else:
        emo_score = next((o["probability"] for o in emo_opts if o["emotion"] == chosen_emo), 0)

    res_score = next((o["score"] for o in res_opts if o["id"] == chosen_res), 0)
    best = next((o for o in res_opts if o["id"] == sc["best_response_id"]), {})
    combined = round((emo_score + res_score) / 2)

    prompt = f"""Signals: {sc['signals']}  Context: {sc['scene']} / {sc['character']}
Student chose emotion "{chosen_emo}" (true: "{true_emo}", score: {emo_score}%)
Student chose response "{chosen_res}" (score: {res_score}%)
Best: "{best.get('action','')}" ({best.get('score',0)}%)

Return ONLY:
{{
  "explanation": "Pattern: [signals] → [emotion] ([prob]%). [Response] scored [X]% because [cause→effect in ≤15 words].",
  "achievement": "Perfect Read"
}}

achievement: "Perfect Read"(≥85) | "Good Pattern"(≥70) | "Pattern Spotter"(≥50) | "Learning Pattern"(<50)
combined score = {combined}"""

    msg = client.messages.create(
        model=MODEL, max_tokens=250,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )
    r = parse_json(msg.content[0].text)
    r["emotion_score"] = emo_score
    r["response_score"] = res_score
    r["combined_score"] = combined
    return jsonify(r)


@app.route("/api/decode", methods=["POST"])
def decode():
    d = request.json
    signals = d.get("signals", [])
    context = d.get("context", "unknown")

    prompt = f"""Location: {context}  Signals: {', '.join(signals)}

Return ONLY (probabilities sum to 100):
{{
  "emotion_probabilities": [
    {{"emotion":"sad",    "probability":45,"emoji":"😢"}},
    {{"emotion":"angry",  "probability":30,"emoji":"😠"}},
    {{"emotion":"worried","probability":15,"emoji":"😟"}},
    {{"emotion":"tired",  "probability":10,"emoji":"😴"}}
  ],
  "recommended_actions": [
    {{"action":"Ask quietly","icon":"💬","visual":"talk",   "score":85}},
    {{"action":"Give space", "icon":"⏳","visual":"wait",   "score":70}},
    {{"action":"Keep working","icon":"📚","visual":"ignore","score":35}}
  ],
  "pattern_rule": "signals → emotion",
  "confidence": 78
}}"""

    msg = client.messages.create(
        model=MODEL, max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )
    return jsonify(parse_json(msg.content[0].text))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
