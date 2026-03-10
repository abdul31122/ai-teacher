"""Books API — বই তালিকা ও ডিটেইল"""
import os
import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# বই তালিকা — নতুন বই যোগ করতে এখানে এড করুন
BOOKS = [
    {
        "id": "bangla-2nd-paper",
        "title": "বাংলা দ্বিতীয় পত্র (ব্যাকরণ)",
        "code": "SSC-2651",
        "class": "SSC",
        "pages": 301,
        "cover": "📕",
        "units": [
            {"id": "unit-01", "title": "ইউনিট—০১: ভাষা (বাংলা ভাষা)", "lessons": [
                {"id": "1.1", "title": "পাঠ ১.১ — ভাষা"},
                {"id": "1.2", "title": "পাঠ ১.২ — বাংলা ভাষারীতি"},
                {"id": "1.3", "title": "পাঠ ১.৩ — বাংলা ব্যাকরণ"},
            ]},
            {"id": "unit-02", "title": "ইউনিট—০২: ধ্বনিতত্ত্ব", "lessons": [
                {"id": "2.1", "title": "পাঠ ২.১ — ধ্বনি ও বর্ণ প্রকরণ"},
                {"id": "2.2", "title": "পাঠ ২.২ — ধ্বনির উচ্চারণবিধি"},
                {"id": "2.3", "title": "পাঠ ২.৩ — ধ্বনি পরিবর্তন"},
            ]},
            {"id": "unit-03", "title": "ইউনিট—০৩: শব্দ প্রকরণ", "lessons": [
                {"id": "3.1", "title": "পাঠ ৩.১ — পুরুষবাচক ও স্ত্রীবাচক শব্দ"},
            ]},
        ],
    }
]


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        book_id = params.get("id", [None])[0]

        if book_id:
            book = next((b for b in BOOKS if b["id"] == book_id), None)
            if book:
                self._send_json(200, book)
            else:
                self._send_json(404, {"error": "বই পাওয়া যায়নি"})
        else:
            # সব বইয়ের তালিকা (ইউনিট ছাড়া)
            book_list = []
            for b in BOOKS:
                book_list.append({
                    "id": b["id"],
                    "title": b["title"],
                    "code": b["code"],
                    "class": b["class"],
                    "pages": b["pages"],
                    "cover": b["cover"],
                })
            self._send_json(200, {"books": book_list})

    def do_OPTIONS(self):
        self._send_cors(204)

    def _send_json(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _send_cors(self, status):
        self.send_response(status)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
