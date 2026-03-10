"""Admin API — ইউজার ব্লক, ব্রডকাস্ট মেসেজ"""
import os
import json
import time
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Admin password — Vercel env এ সেট করুন
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "").strip()

# ডেটা ফাইল পাথ (Vercel-এ /tmp ব্যবহার করতে হয়)
BLOCKED_FILE = "/tmp/blocked_users.json"
BROADCAST_FILE = "/tmp/broadcast.json"


def load_json(path, default=None):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except:
        return default if default is not None else {}


def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, ensure_ascii=False)


def check_admin(headers):
    """Admin password চেক"""
    auth = headers.get("X-Admin-Key", "")
    if not ADMIN_PASSWORD or auth != ADMIN_PASSWORD:
        return False
    return True


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        action = params.get("action", ["status"])[0]

        # ইউজার-ফেসিং: ব্লক চেক + ব্রডকাস্ট মেসেজ
        if action == "check":
            user_id = params.get("user_id", [""])[0]
            blocked = load_json(BLOCKED_FILE, {})
            broadcast = load_json(BROADCAST_FILE, {"message": "", "active": False})

            is_blocked = False
            if user_id and user_id in blocked:
                block_info = blocked[user_id]
                # সময় শেষ হয়ে গেলে আনব্লক
                if block_info.get("until", 0) > time.time():
                    is_blocked = True

            self._send_json(200, {
                "blocked": is_blocked,
                "broadcast": broadcast if broadcast.get("active") else None
            })
            return

        # Admin: ব্লক লিস্ট দেখাও
        if action == "blocked_list":
            if not check_admin(self.headers):
                self._send_json(403, {"error": "Unauthorized"})
                return
            blocked = load_json(BLOCKED_FILE, {})
            self._send_json(200, {"blocked": blocked})
            return

        # Admin: ব্রডকাস্ট মেসেজ দেখাও
        if action == "broadcast_get":
            if not check_admin(self.headers):
                self._send_json(403, {"error": "Unauthorized"})
                return
            broadcast = load_json(BROADCAST_FILE, {"message": "", "active": False})
            self._send_json(200, broadcast)
            return

        self._send_json(200, {"status": "AI Teacher Admin API"})

    def do_POST(self):
        if not check_admin(self.headers):
            self._send_json(403, {"error": "Unauthorized"})
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        data = json.loads(body)
        action = data.get("action", "")

        # ইউজার ব্লক
        if action == "block":
            user_id = data.get("user_id", "")
            minutes = data.get("minutes", 30)  # ডিফল্ট ৩০ মিনিট
            reason = data.get("reason", "")

            if not user_id:
                self._send_json(400, {"error": "user_id দিন"})
                return

            blocked = load_json(BLOCKED_FILE, {})
            blocked[user_id] = {
                "until": time.time() + (minutes * 60),
                "minutes": minutes,
                "reason": reason,
                "blocked_at": time.time()
            }
            save_json(BLOCKED_FILE, blocked)
            self._send_json(200, {"success": True, "message": f"{user_id} ব্লক হয়েছে {minutes} মিনিটের জন্য"})
            return

        # ইউজার আনব্লক
        if action == "unblock":
            user_id = data.get("user_id", "")
            blocked = load_json(BLOCKED_FILE, {})
            if user_id in blocked:
                del blocked[user_id]
                save_json(BLOCKED_FILE, blocked)
            self._send_json(200, {"success": True, "message": f"{user_id} আনব্লক হয়েছে"})
            return

        # ব্রডকাস্ট মেসেজ সেট
        if action == "broadcast":
            message = data.get("message", "")
            active = data.get("active", True)
            save_json(BROADCAST_FILE, {
                "message": message,
                "active": active,
                "updated_at": time.time()
            })
            self._send_json(200, {"success": True, "message": "ব্রডকাস্ট আপডেট হয়েছে"})
            return

        self._send_json(400, {"error": "Unknown action"})

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Admin-Key")
        self.end_headers()

    def _send_json(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Admin-Key")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
