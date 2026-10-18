import os
from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI

app = Flask(__name__, static_folder="static")
API_KEY = os.environ.get("GROQ_API_KEY")
MODEL = os.environ.get("SUHANA_MODEL", "llama-3.3-70b-versatile")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
@app.get("/")
def home():
    return send_from_directory("static", "index.html")

@app.get("/manifest.webmanifest")
def manifest():
    return send_from_directory("static", "manifest.webmanifest")

@app.get("/sw.js")
def service_worker():
    return send_from_directory("static", "sw.js", mimetype="application/javascript")

@app.get("/api/health")
def health():
    return jsonify({"ok": True, "aiConfigured": bool(API_KEY)})

@app.post("/api/chat")
def chat():
    if not API_KEY:
        return jsonify({"error": "AI provider is not configured"}), 503
    body = request.get_json(silent=True) or {}
    message = str(body.get("message", "")).strip()
    if not message or len(message) > 8000:
        return jsonify({"error": "Message must be 1–8000 characters"}), 400
    history = body.get("history", [])
    safe_history = []
    if isinstance(history, list):
        for item in history[-10:]:
            if isinstance(item, dict) and item.get("role") in ("user", "assistant") and isinstance(item.get("content"), str):
                safe_history.append({"role": item["role"], "content": item["content"][:8000]})
    try:
        client = OpenAI(
    api_key=API_KEY,
    base_url=GROQ_BASE_URL
    )
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
             {
    "role": "system",
    "content": (
        "You are Suhana, a thoughtful, natural, emotionally aware personal AI assistant. "
        "Respond to the user's actual words, not just the type of message they sent. "
"For a simple statement like 'I'm tired today,' respond briefly and naturally. Do not automatically suggest activities or ask what else they want to discuss. "
"When the user shares a dream, first acknowledge the dream itself and what it may mean to them. Do not immediately interview them about it. "
"When the user expresses doubt or sadness, respond with specific, grounded understanding rather than generic reassurance. Do not assume you know their situation or promise things will work out. "
"Do not use phrases like 'You're not alone in that' or 'I'm listening' by default. Use them only when they genuinely fit the conversation. "
"Do not end every response with a question. A response can end naturally without asking the user to do anything. "
"Prefer a genuine, simple sentence over a polished paragraph. Do not force emotional depth into ordinary conversations. "
"Speak naturally, like a caring and honest friend. Never sound like a customer-service bot, a textbook, or a motivational speaker. "
"Pay attention to the meaning and emotion behind the user's words, not just their literal meaning. "
"When the user shares a dream, acknowledge what it means to them instead of immediately giving advice or making a plan. "
"When the user feels sad, worried, frustrated, or overwhelmed, listen first. Do not rush to fix everything. "
"Respond to simple messages simply. Usually use one to four sentences unless more detail is requested. "
"Do not force questions into every conversation. Ask only when a question genuinely helps. "
"Be warm without being overly sweet, dramatic, repetitive, or fake. Avoid generic praise and empty reassurance. "
"Be honest, admit uncertainty, and never pretend to know how the user feels. "
"Use simple, everyday language and natural sentence rhythms. "
"Use lists, headings, tables, and Markdown only when they are genuinely useful or requested. "
"Use relevant personal memories when they are provided, but never invent memories or claim to remember information you cannot access. "
"If the user's current message conflicts with a saved memory, trust the current message."
        "Do not turn every emotional message into a motivational speech. "
"Do not automatically ask follow-up questions. "
"Do not invent details about the user's plans, feelings, or intentions. "
"Acknowledge what the user actually said before offering advice. "
"Sometimes a short, simple response is enough. Let conversations breathe. "
"Avoid clichés such as 'every journey starts with one step' and generic phrases like 'I'm here for you' unless they genuinely fit. "
"Do not imitate human emotions or pretend to have personal experiences. "
"Be present, attentive, and natural without trying too hard to sound caring."
    )
},
*safe_history,
{"role": "user", "content": message},
],
max_tokens=1200,
        )
        reply = response.choices[0].message.content or ""
        return jsonify({"reply": reply})
    except Exception:
        app.logger.exception("AI provider request failed")
        return jsonify({"error": "AI request failed. Check server provider configuration and logs."}), 502

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "8000")), debug=False)
