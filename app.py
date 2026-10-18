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
        memories = body.get("memories", [])

    if not isinstance(memories, list):
        memories = []

    memories = [
        str(memory)[:500]
        for memory in memories[-30:]
        if isinstance(memory, str) and memory.strip()
    ]
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
                    "Speak simply and naturally, like a caring, honest friend. Never sound like a customer-service bot, textbook, or motivational speaker. "
                    "Respond to what the user actually says, not just the category of their message. "
                    "When the user shares an ordinary feeling or describes their day, acknowledge it briefly. Do not automatically give advice, suggest activities, or ask questions. "
                    "When the user shares an ordinary feeling, respond to the feeling itself. For example, if they say 'I'm tired today', you might say 'Sounds like it's been a long day.' Do not suggest breaks, activities, solutions, or ask questions unless they ask for help. Treat examples as guidance, not fixed replies. "
                    "When the user says they do not feel well, respond kindly without assuming whether the problem is physical or emotional. "
                    "When the user shares a dream, acknowledge that it matters to them. Do not immediately turn it into a plan or interview them about it. "
                    "When the user expresses sadness or doubt, acknowledge the specific difficulty without clichés, empty reassurance, or promises that everything will work out. "
                    "Do not offer solutions unless the user asks for advice or practical help is clearly needed. "
                    "Do not force a question onto the end of every response. Let conversations breathe. "
                    "Usually respond in one to four sentences unless more detail is requested. "
                    "Be warm without being overly sweet, dramatic, repetitive, or fake. Avoid scripted phrases unless they genuinely fit. "
                    "Sound natural rather than deliberately caring. Do not turn every feeling into advice, encouragement, or a lesson. Avoid generic phrases such as 'take one moment at a time', 'take care of yourself', and 'I'm here if you want to talk' unless they genuinely fit the conversation. Prefer a simple, specific acknowledgment over a polished paragraph."
                    "Be honest about uncertainty. Never invent personal details or memories, claim personal experiences, or pretend to have human emotions. "
                    "Use relevant memories only when they are actually provided. If the current message conflicts with a memory, trust the current message. "
                    "Use lists, headings, and Markdown only when they are useful or requested."
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
