"""AI Teacher Chat API — Vercel Serverless Function"""
import os
import json
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler

SYSTEM_PROMPT = """بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ

তুমি "AI Teacher" — একজন বন্ধুসুলভ, ধৈর্যশীল বাংলা টিউটর।
তুমি বাংলাদেশ উন্মুক্ত বিশ্ববিদ্যালয়ের SSC প্রোগ্রামের ছাত্রদের সাহায্য করো।
তোমার বিষয়: বাংলা দ্বিতীয় পত্র (ব্যাকরণ) — SSC-2651

📌 প্রতিটা উত্তরের শুরুতে: بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ

📌 ভাষা নিয়ম:
- বাংলায় প্রশ্ন → বাংলায় উত্তর
- ইংরেজিতে প্রশ্ন → ইংরেজিতে উত্তর
- বাংলিশ বুঝবে: "phat 2.3 bujhiye dao" = "পাঠ ২.৩ বুঝিয়ে দাও"
- "Explain unit 2" → English answer (but book quotes in Bengali)
- ইউজার যে ভাষায় প্রশ্ন করবে সেই ভাষায় উত্তর দেবে

📌 MCQ: ৫-১০টা, উত্তর আলাদায়, স্কোরিং সহ
📌 সম্ভাষণ: আসসালামু আলাইকুম / আল্লাহ হাফেজ
📌 পড়ালেখার বাইরে: "আমি AI Teacher 😊 পড়ালেখায় সাহায্য করি!"
📌 উৎসাহ দেবে, ইমোজি ব্যবহার করবে

📌 বইয়ের বিষয়বস্তু (বাংলা ব্যাকরণ):
ইউনিট ০১: ভাষা | ইউনিট ০২: ধ্বনিতত্ত্ব | ইউনিট ০৩: শব্দ প্রকরণ
ইউনিট ০৪: পদ প্রকরণ | ইউনিট ০৫: বাক্য প্রকরণ | ইউনিট ০৬: বানান ও বিরাম
ইউনিট ০৭: ব্যাকরণিক শব্দ শ্রেণি
তুমি বাংলা ব্যাকরণে বিশেষজ্ঞ।
"""


def call_groq(messages):
    """Groq API কল"""
    api_key = os.environ.get("GROQ_API_KEY", "").strip()

    payload = json.dumps({
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 2048
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json",
            "User-Agent": "AI-Teacher/1.0"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise Exception(f"Groq API {e.code}: {body}")


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)

            messages = data.get("messages", [])
            book_context = data.get("book_context", "")

            if not messages:
                self._send_json(400, {"error": "messages ফাঁকা"})
                return

            system_msg = SYSTEM_PROMPT
            if book_context:
                system_msg += f"\n\n📍 ছাত্র: {book_context}"

            full_messages = [{"role": "system", "content": system_msg}]
            full_messages.extend(messages)

            reply = call_groq(full_messages)
            self._send_json(200, {"reply": reply})

        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _send_json(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
