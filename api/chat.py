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
- ইংরেজিতে প্রশ্ন → ইংরেজিতে উত্তর (বইয়ের উদ্ধৃতি বাংলায়)
- বাংলিশ বুঝবে: "phat 2.3 bujhiye dao" = "পাঠ ২.৩ বুঝিয়ে দাও"

📌 বই থেকে টেক্সট পেলে:
- বইয়ের টেক্সট বিজয় থেকে কনভার্ট করা, কিছু ভুল থাকতে পারে
- ভুল থাকলে নিজের বাংলা ব্যাকরণ জ্ঞান দিয়ে সংশোধন করে উত্তর দাও
- বইতে না থাকলে: "এটা বইতে সরাসরি নেই, তবে আমার জ্ঞান থেকে বলি..."

📌 MCQ পরীক্ষা ও স্কোরিং:
- ৫-১০টা MCQ, উত্তর আলাদায়
- ইউজার উত্তর দিলে ✅❌ ও স্কোর
- ৯-১০/১০ → "ম্যাশাআল্লাহ! অসাধারণ! 🌟🏆"
- ৭-৮/১০ → "বাহ! অনেক ভালো! 👏💪"
- ৫-৬/১০ → "ভালো চেষ্টা! 😊"
- ৪ বা কম → "চিন্তা নেই! ভুল থেকেই শেখা! 🤗💪"

📌 সম্ভাষণ: "আসসালামু আলাইকুম! 😊" / "আল্লাহ হাফেজ! 🤲"
📌 পড়ালেখার বাইরে: "আমি AI Teacher 😊 পড়ালেখায় সাহায্য করি!"
📌 উৎসাহ: ইমোজি 😊📚✅💪

📌 বইয়ের বিষয়বস্তু (বাংলা ব্যাকরণ):
- ইউনিট ০১: ভাষা, বাংলা ভাষারীতি, বাংলা ব্যাকরণ
- ইউনিট ০২: ধ্বনিতত্ত্ব — ধ্বনি ও বর্ণ, উচ্চারণবিধি, ধ্বনি পরিবর্তন
- ইউনিট ০৩: শব্দ প্রকরণ
- ইউনিট ০৪: পদ প্রকরণ — বিশেষ্য, বিশেষণ, সর্বনাম, ক্রিয়া, অব্যয়
- ইউনিট ০৫: বাক্য প্রকরণ
- ইউনিট ০৬: বানান ও বিরাম চিহ্ন
- ইউনিট ০৭: ব্যাকরণিক শব্দ শ্রেণি
তুমি এই সব বিষয়ে বিশেষজ্ঞ। বই + নিজের জ্ঞান থেকে উত্তর দেবে।
"""


def call_groq(messages):
    """Groq API কল — urllib দিয়ে (কোনো SDK লাগে না)"""
    api_key = os.environ.get("GROQ_API_KEY", "")
    
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
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )
    
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]


# বইয়ের চাঙ্ক লোড
_chunks = None

def load_chunks():
    global _chunks
    if _chunks is not None:
        return _chunks
    try:
        p = os.path.join(os.path.dirname(__file__), '..', 'data', 'bangla-2nd-paper_chunks.json')
        with open(p, 'r', encoding='utf-8') as f:
            _chunks = json.load(f)
    except:
        _chunks = []
    return _chunks


def search_chunks(query, top_k=3):
    """কীওয়ার্ড সার্চ — প্রাসঙ্গিক চাঙ্ক খোঁজে"""
    chunks = load_chunks()
    if not chunks:
        return ""
    keywords = query.lower().split()
    scored = []
    for chunk in chunks:
        text = chunk.get('text', '').lower()
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scored.append((score, chunk))
    scored.sort(key=lambda x: -x[0])
    results = []
    for score, chunk in scored[:top_k]:
        results.append(f"[পাতা {chunk['page']}]: {chunk['text'][:400]}")
    return "\n\n".join(results)


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

            # বই সার্চ
            last_msg = messages[-1].get('content', '')
            book_search = search_chunks(last_msg)
            
            system_msg = SYSTEM_PROMPT
            if book_search:
                system_msg += f"\n\n📚 বই থেকে:\n{book_search}"
            if book_context:
                system_msg += f"\n\n📍 ছাত্র: {book_context}"

            full_messages = [{"role": "system", "content": system_msg}]
            full_messages.extend(messages)

            reply = call_groq(full_messages)
            self._send_json(200, {"reply": reply})

        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def do_OPTIONS(self):
        self._send_cors(204)

    def _send_json(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _send_cors(self, status):
        self.send_response(status)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
