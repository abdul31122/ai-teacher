import os, json
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        key = os.environ.get("GROQ_API_KEY", "NOT_SET")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        # শুধু প্রথম ও শেষ ৪ অক্ষর দেখাই (নিরাপত্তার জন্য)
        masked = f"{key[:4]}...{key[-4:]}" if len(key) > 8 else "TOO_SHORT"
        self.wfile.write(json.dumps({
            "key_length": len(key),
            "key_masked": masked,
            "has_newline": "\\n" in key,
            "repr": repr(key[:10])
        }).encode())
