import os
from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI

app = Flask(__name__, static_folder="static")
API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL = os.environ.get("SUHANA_MODEL", "gemini-3.8-flash")
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

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
    base_url=GEMINI_BASE_URL
                                     )
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are Suhana, a warm, honest, practical personal AI assistant. Explain clearly, admit uncertainty, and never claim to have taken actions you have not taken."},
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
