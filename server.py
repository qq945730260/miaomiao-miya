"""Pet Shop Server V6 - JSON storage for persistence"""
import json, os, secrets, time, re, subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_RENDER_VOL = os.environ.get("RENDER_EXTERNAL_VOLUME", "").strip() or "/home/miaomiao/data"
if _RENDER_VOL:
    DATA_DIR = _RENDER_VOL
    UPLOAD_DIR = os.path.join(_RENDER_VOL, "uploads")
else:
    DATA_DIR = os.path.join(BASE_DIR, "data")
    UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
STATIC_DIR = os.path.join(BASE_DIR, "static")
STORE_FILE = os.path.join(DATA_DIR, "store.json")
ADMIN_USER = "xuxu"
ADMIN_PASS = "5361172"
SESSION_TTL = 86400
MAX_PRODUCTS = 30
BLOCKED_DOMAIN = "miaomiao.au0817.dpdns.org"
ORDER_RETENTION_DAYS = 7

def load_store():
    """Load store data from JSON file. Never reset to defaults if file exists."""
    if os.path.exists(STORE_FILE):
        try:
            with open(STORE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Ensure all expected keys exist (migrate old formats)
            data.setdefault("products", [])
            data.setdefault("categories", [])
            data.setdefault("orders", [])
            data.setdefault("settings", {})
            data.setdefault("admin", {"username": ADMIN_USER, "password": ADMIN_PASS})
            return data
        except Exception as e:
            print("ERROR loading store:", e, flush=True)
    # Only create default on first run when file truly doesn't exist
    return {
        "products": [],
        "categories": [],
        "orders": [],
        "settings": {
            "site_title": "喵喵咪丫",
            "shop_description": "",
            "wechat_pay_qr": "",
            "alipay_qr": "",
            "wechat_qr": "",
            "shop_logo": ""
        },
        "admin": {"username": ADMIN_USER, "password": ADMIN_PASS}
    }

def save_store(store):
    """Save store data to JSON file and commit to git."""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(STORE_FILE, "w", encoding="utf-8") as f:
            json.dump(store, f, ensure_ascii=False, indent=2)
        auto_commit()
    except Exception as e:
        print("ERROR saving store:", e, flush=True)

def get_next_id(items):
    """Get next sequential ID for a list of items."""
    if not items:
        return 1
    return max(item.get("id", 0) for item in items) + 1

def generate_order_number():
    """Generate order number like 26091401 (date + sequence)"""
    now = time.strftime("%y%m%d")
    # Get today's orders count to determine sequence
    store_file = STORE_FILE
    seq = 1
    if os.path.exists(store_file):
        try:
            with open(store_file, "r", encoding="utf-8") as f:
                store = json.load(f)
            today = time.strftime("%Y-%m-%d")
            today_orders = [o for o in store.get("orders", []) if o.get("created_at", "").startswith(today)]
            seq = len(today_orders) + 1
        except:
            pass
    return now + str(seq).zfill(2)

SYNC_LOG = os.path.join(BASE_DIR, "data", "sync.log")

def log_sync(msg):
    try:
        os.makedirs(os.path.dirname(SYNC_LOG), exist_ok=True)
        with open(SYNC_LOG, "a", encoding="utf-8") as f:
            f.write(time.strftime("%Y-%m-%d %H:%M:%S") + " " + msg + "\n")
    except Exception:
        pass

def auto_commit():
    """Commit and push data to git."""
    token = os.environ.get("GH_TOKEN", "").strip()
    if not token:
        log_sync("SKIP: GH_TOKEN not set")
        return
    try:
        r = subprocess.run(["git", "-c", "safe.directory=*", "add", "-A", "data/", "uploads/"],
            capture_output=True, timeout=10, cwd=BASE_DIR)

        r2 = subprocess.run(["git", "-c", "safe.directory=*", "commit", "-q", "--allow-empty", "-m", "auto-commit data"],
            capture_output=True, timeout=10, cwd=BASE_DIR)
        if b"nothing" not in r2.stdout and b"nothing" not in r2.stderr:
            # Use credential helper to avoid token in URL (triggers GH secret scan)
            cred_file = os.path.join(BASE_DIR, ".git", ".credentials")
            os.makedirs(os.path.join(BASE_DIR, ".git"), exist_ok=True)
            with open(cred_file, "w") as cf:
                cf.write("https://x-access-token:" + token + "@github.com\n")
            try:
                r3 = subprocess.run(["git", "-c", "safe.directory=*",
                    "-c", "credential.helper=store --file=" + cred_file,
                    "push", "origin", "v7"],
                    capture_output=True, timeout=30, cwd=BASE_DIR)
            finally:
                try: os.remove(cred_file)
                except: pass
                if r3.returncode == 0:
                    log_sync("OK: pushed to v7")
                else:
                    err = r3.stderr.decode("utf-8", errors="replace")[:300]
                    log_sync("FAIL: " + err)
    except Exception as e:
        log_sync("EXC: " + str(e))

def ensure_git_remote():
    """Ensure git remote origin is configured."""
    try:
        r = subprocess.run(["git", "-c", "safe.directory=*", "remote", "get-url", "origin"],
            capture_output=True, text=True, timeout=5, cwd=BASE_DIR)
        if r.returncode != 0:
            # Remote not configured, set it up
            token = os.environ.get("GH_TOKEN", "").strip()
            if token:
                url = "https://x-access-token:" + token + "@github.com/qq945730260/miaomiao-miya.git"
                subprocess.run(["git", "-c", "safe.directory=*", "remote", "add", "origin", url],
                    capture_output=True, timeout=5, cwd=BASE_DIR)
                log_sync("SETUP: git remote origin configured")
    except Exception as e:
        log_sync("SETUP WARN: " + str(e))


def pull_data_from_git():
    """Pull latest data from git on startup."""
    token = os.environ.get("GH_TOKEN", "").strip()
    if not token:
        log_sync("SKIP: GH_TOKEN not set")
        return
    try:
        cred_file = os.path.join(BASE_DIR, ".git", ".credentials")
        os.makedirs(os.path.join(BASE_DIR, ".git"), exist_ok=True)
        with open(cred_file, "w") as cf:
            cf.write("https://x-access-token:" + token + "@github.com\n")
        try:
            # Fetch first to check status
            r_fetch = subprocess.run(["git", "-c", "safe.directory=*",
                "-c", "credential.helper=store --file=" + cred_file,
                "fetch", "origin", "v7"],
                capture_output=True, timeout=15, cwd=BASE_DIR)
            if r_fetch.returncode != 0:
                log_sync("FETCH FAIL: " + r_fetch.stderr.decode("utf-8", errors="replace")[:200])
                return
            # Then pull
            r = subprocess.run(["git", "-c", "safe.directory=*",
                "-c", "credential.helper=store --file=" + cred_file,
                "pull", "--ff-only", "origin", "v7"],
                capture_output=True, timeout=30, cwd=BASE_DIR)
        finally:
            try: os.remove(cred_file)
            except: pass
        if r.returncode == 0:
            log_sync("OK: pulled v7 on startup")
        else:
            err = r.stderr.decode("utf-8", errors="replace")[:300]
            log_sync("PULL FAIL: " + err)
            # Try force pull as fallback
            log_sync("TRYING FORCE PULL v7...")
            r2 = subprocess.run(["git", "-c", "safe.directory=*",
                "-c", "credential.helper=store --file=" + cred_file,
                "pull", "--force", "origin", "v7"],
                capture_output=True, timeout=30, cwd=BASE_DIR)
            if r2.returncode == 0:
                log_sync("OK: force pulled v7")
            else:
                log_sync("FORCE PULL FAILED: " + r2.stderr.decode("utf-8", errors="replace")[:200])
    except Exception as e:
        log_sync("EXCEPTION: " + str(e))


def clean_expired(store):
    """Remove expired orders."""
    cutoff = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time() - ORDER_RETENTION_DAYS * 86400))
    store["orders"] = [o for o in store.get("orders", []) if o.get("created_at", "") >= cutoff]
    return store

def send_json(h, data, status=200):
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    h.send_response(status)
    h.send_header("Content-Type", "application/json; charset=utf-8")
    h.send_header("Access-Control-Allow-Origin", "*")
    h.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    h.send_header("Access-Control-Allow-Headers", "Content-Type")
    h.send_header("Content-Length", str(len(body)))
    h.end_headers()
    h.wfile.write(body)

def require_auth(h):
    for part in h.headers.get("Cookie", "").split(";"):
        part = part.strip()
        if part.startswith("session="):
            token = part[8:]
            fp = os.path.join(DATA_DIR, "session_" + token)
            if os.path.exists(fp):
                try:
                    if time.time() - os.path.getmtime(fp) < SESSION_TTL:
                        return True
                except Exception:
                    pass
    return False

def parse_body(h):
    n = int(h.headers.get("Content-Length", 0))
    if n == 0:
        return {}
    try:
        return json.loads(h.rfile.read(n))
    except Exception:
        return {}

class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        p = urlparse(self.path)
        path = p.path.rstrip("/") or "/"
        store = load_store()
        
        if path in ("/", "/index"):
            self.serve(os.path.join(STATIC_DIR, "index.html"), "text/html; charset=utf-8")
        elif path == "/product":
            self.serve(os.path.join(STATIC_DIR, "product.html"), "text/html; charset=utf-8")
        elif path == "/admin":
            host = self.headers.get("Host", "")
            if BLOCKED_DOMAIN and host == BLOCKED_DOMAIN:
                return send_json(self, {"error": "forbidden"}, 403)
            self.serve(os.path.join(STATIC_DIR, "admin.html"), "text/html; charset=utf-8")
        elif path == "/api/products":
            qs = parse_qs(p.query)
            if "id" in qs:
                prod = next((pr for pr in store.get("products", []) if pr["id"] == int(qs["id"][0])), None)
                send_json(self, prod if prod else {}, 404 if not prod else 200)
            else:
                send_json(self, store.get("products", []))
        elif path == "/api/settings":
            send_json(self, store.get("settings", {}))
        elif path == "/api/admin/check":
            send_json(self, {"auth": require_auth(self)})
        elif path == "/api/admin/sync":
            if not require_auth(self):
                return send_json(self, {"error": "unauthorized"}, 401)
            try:
                pull_data_from_git()
                store = load_store()
                auto_commit()
                send_json(self, {"ok": True, "message": "同步完成"})
            except Exception as e:
                log_sync("SYNC ERR: " + str(e))
                send_json(self, {"ok": False, "message": str(e)}, 500)
        elif path == "/api/admin/payment_qrcodes":
            if not require_auth(self):
                return send_json(self, {"error": "unauthorized"}, 401)
            settings = store.get("settings", {})
            send_json(self, {"wechat_pay_qr": settings.get("wechat_pay_qr", ""),
                           "alipay_qr": settings.get("alipay_qr", "")})
        elif path == "/api/categories":
            send_json(self, store.get("categories", []))
        elif path == "/api/orders":
            if not require_auth(self):
                return send_json(self, {"error": "unauthorized"}, 401)
            store = clean_expired(store)
            orders = store.get("orders", [])
            result = []
            for o in orders:
                prod = next((p for p in store.get("products", []) if p["id"] == o["product_id"]), {})
                result.append({**o, "product_name": prod.get("name", ""),
                             "product_title": prod.get("title", ""),
                             "product_image": prod.get("image", "")})
            result.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            send_json(self, result)
        elif path == "/api/sold":
            # Public endpoint: return sold quantity per product (only completed orders)
            orders = store.get("orders", [])
            sold = {}
            for o in orders:
                if o.get("status") == "completed":
                    pid = o.get("product_id")
                    sold[pid] = sold.get(pid, 0) + o.get("qty", 1)
            send_json(self, sold)
        elif path == "/uploads":
            files = os.listdir(UPLOAD_DIR) if os.path.exists(UPLOAD_DIR) else []
            send_json(self, [f for f in files if not f.startswith(".")])
        elif path == "/api/debug":
            db_size = os.path.getsize(STORE_FILE) if os.path.exists(STORE_FILE) else 0
            upload_count = len([f for f in os.listdir(UPLOAD_DIR) if not f.startswith(".")]) if os.path.exists(UPLOAD_DIR) else 0
            sync_log_exists = os.path.exists(SYNC_LOG)
            sync_log = ""
            if sync_log_exists:
                with open(SYNC_LOG, "r", encoding="utf-8") as f:
                    sync_log = f.read()[-1500:]
            send_json(self, {
                "db_size": db_size,
                "upload_count": upload_count,
                "product_count": len(store.get("products", [])),
                "category_count": len(store.get("categories", [])),
                "order_count": len(store.get("orders", [])),
                "gh_token_set": bool(os.environ.get("GH_TOKEN", "").strip() or os.environ.get("GITHUB_TOKEN", "").strip()),
                "sync_log_exists": sync_log_exists,
                "sync_log": sync_log,
            })
        elif path.startswith("/static/"):
            self.serve(os.path.join(BASE_DIR, path.lstrip("/")))
        elif path.startswith("/uploads/"):
            self.serve(os.path.join(BASE_DIR, path.lstrip("/")))
        else:
            self.send_error(404)

    def do_POST(self):
        p = urlparse(self.path)
        path = p.path.rstrip("/") or "/"
        store = load_store()
        
        if path == "/api/admin/login":
            b = parse_body(self)
            admin = store.get("admin", {"username": ADMIN_USER, "password": ADMIN_PASS})
            if b.get("username") == admin["username"] and b.get("password") == admin["password"]:
                tok = secrets.token_hex(16)
                fp = os.path.join(DATA_DIR, "session_" + tok)
                open(fp, "w").close()
                body = json.dumps({"ok": True}, ensure_ascii=False).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Set-Cookie", "session=" + tok + "; Path=/; Max-Age=" + str(SESSION_TTL))
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                send_json(self, {"error": "密码错误"}, 401)
        elif path == "/api/admin/change_password":
            if not require_auth(self):
                return send_json(self, {"error": "unauthorized"}, 401)
            b = parse_body(self)
            admin = store.get("admin", {})
            old_pwd = b.get("old_password", "")
            new_pwd = b.get("new_password", "")
            if not old_pwd or not new_pwd:
                return send_json(self, {"error": "missing fields"}, 400)
            if admin.get("password") == old_pwd:
                store["admin"]["password"] = new_pwd
                save_store(store)
                return send_json(self, {"ok": True})
            return send_json(self, {"error": "old password wrong"}, 401)

        elif path == "/api/categories/batch" and require_auth(self):
            b = parse_body(self)
            cats = b if isinstance(b, list) else b.get("categories", [])
            for cat in cats:
                cid = str(cat.get("id", ""))
                cname = cat.get("name", "")
                csort = cat.get("sort_order", 0)
                if cid and cname:
                    store_cats = store.get("categories", [])
                    for sc in store_cats:
                        if str(sc["id"]) == cid:
                            sc["name"] = cname
                            sc["sort_order"] = int(csort)
                            break
            store["categories"] = store_cats
            save_store(store)
            send_json(self, {"ok": True})
        elif path == "/api/categories" and require_auth(self):
            b = parse_body(self)
            name = b.get("name", "").strip()
            if not name:
                return send_json(self, {"error": "missing name"}, 400)
            categories = store.get("categories", [])
            max_order = max((c.get("sort_order", 0) for c in categories), default=-1)
            new_id = get_next_id(categories)
            categories.append({"id": new_id, "name": name, "sort_order": int(b.get("sort_order", max_order + 1))})
            store["categories"] = categories
            save_store(store)
            send_json(self, {"id": new_id, "name": name, "sort_order": categories[-1]["sort_order"]}, 201)
        elif path == "/api/products":
            if not require_auth(self):
                return send_json(self, {"error": "unauthorized"}, 401)
            products = store.get("products", [])
            if len(products) >= MAX_PRODUCTS:
                return send_json(self, {"error": "商品数量已达上限 (" + str(MAX_PRODUCTS) + ")", "count": len(products)}, 400)
            b = parse_body(self)
            new_id = get_next_id(products)
            products.append({
                "id": new_id,
                "name": b.get("name", ""),
                "title": (b.get("title", "") or "").strip()[:60],
                "category": b.get("category", ""),
                "price": float(b.get("price", 0)),
                "stock": int(b.get("stock", 0)),
                "image": b.get("image", "placeholder.jpg"),
                "detail_image": b.get("detail_image", ""),
                "description": b.get("description", ""),
                "wechat": b.get("wechat", ""),
                "qq": b.get("qq", "")
            })
            store["products"] = products
            save_store(store)
            send_json(self, products[-1], 201)
        elif path == "/api/upload":
            if not require_auth(self):
                return send_json(self, {"error": "unauthorized"}, 401)
            ct = self.headers.get("Content-Type", "")
            m = re.search(r"boundary=(.+)", ct)
            if not m:
                return send_json(self, {"error": "missing boundary"}, 400)
            bound = m.group(1).encode()
            ln = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(ln)
            for part in body.split(b"--" + bound):
                if part.strip() == b"" or part.startswith(b"--"):
                    continue
                hr, _, data = part.partition(b"\r\n\r\n")
                hs = hr.decode("utf-8", errors="replace")
                nm = re.search(r'name="([^"]+)"', hs)
                fm = re.search(r'filename="([^"]+)"', hs)
                if nm and fm and nm.group(1) == "image":
                    fn = os.path.basename(fm.group(1)).replace(" ", "_")
                    ext = os.path.splitext(fn)[1].lower() or ".jpg"
                    if ext not in {".jpg",".jpeg",".png",".gif",".webp",".svg"}:
                        return send_json(self, {"error": "bad ext"}, 400)
                    sn = secrets.token_hex(8) + ext
                    os.makedirs(UPLOAD_DIR, exist_ok=True)
                    with open(os.path.join(UPLOAD_DIR, sn), "wb") as f:
                        f.write(data.rstrip(b"\r\n"))
                    auto_commit()
                    return send_json(self, {"filename": sn})
            send_json(self, {"error": "no image"}, 400)
        elif path == "/api/settings" and require_auth(self):
            b = parse_body(self)
            settings = store.get("settings", {})
            for k, v in b.items():
                settings[k] = str(v)
            store["settings"] = settings
            save_store(store)
            send_json(self, {"ok": True})
        elif path == "/api/order/create":
            b = parse_body(self)
            email = (b.get("email") or "").strip().lower()
            password = (b.get("password") or "").strip()
            product_id = b.get("product_id")
            qty = int(b.get("qty", 1))
            if not email or not password or product_id is None:
                return send_json(self, {"error": "missing fields"}, 400)
            if not re.match(r"^[0-9]{6,8}$", password):
                return send_json(self, {"error": "查询密码为6-8位数字"}, 400)
            products = store.get("products", [])
            product = next((p for p in products if p["id"] == int(product_id)), None)
            if not product:
                return send_json(self, {"error": "商品不存在"}, 404)
            total = round(float(product["price"]) * qty, 2)
            now = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            orders = store.get("orders", [])
            order_number = generate_order_number()
            new_id = get_next_id(orders)
            orders.append({
                "order_number": order_number,
                "email": email,
                "password": password,
                "product_id": int(product_id),
                "qty": qty,
                "total": total,
                "status": "pending",
                "created_at": now
            })
            store["orders"] = orders
            save_store(store)
            send_json(self, {"ok": True, "order_id": order_number, "total": total, "product_name": product["name"]})
        elif path == "/api/order/query":
            b = parse_body(self)
            email = (b.get("email") or "").strip().lower()
            password = (b.get("password") or "").strip()
            if not email or not password:
                return send_json(self, {"error": "missing fields"}, 400)
            store = clean_expired(store)
            orders = store.get("orders", [])
            order = next((o for o in orders if o.get("email") == email and o.get("password") == password), None)
            if order:
                # Remove status from response
                result = {k: v for k, v in order.items() if k != "status"}
                send_json(self, result)
            else:
                send_json(self, {"error": "未找到订单，请确认邮箱和密码是否正确"}, 404)
        elif path == "/api/order/confirm":
            b = parse_body(self)
            oid = b.get("order_id")
            if not oid:
                return send_json(self, {"error": "missing order_id"}, 400)
            orders = store.get("orders", [])
            order = next((o for o in orders if o.get("order_number") == str(oid)), None)
            if not order:
                return send_json(self, {"error": "订单不存在"}, 404)
            if order.get("status") == "completed":
                return send_json(self, {"ok": True, "already": True})
            products = store.get("products", [])
            for prod in products:
                if prod["id"] == order["product_id"]:
                    prod["stock"] = max(0, prod["stock"] - order["qty"])
                    break
            order["status"] = "completed"
            store["orders"] = orders
            store["products"] = products
            save_store(store)
            send_json(self, {"ok": True})
        else:
            self.send_error(404)

    def do_PUT(self):
        p = urlparse(self.path)
        path = p.path.rstrip("/") or "/"
        qs = parse_qs(p.query)
        store = load_store()
        
        if path == "/api/products" and require_auth(self):
            pid = qs.get("id", [None])[0]
            if not pid:
                return send_json(self, {"error": "missing id"}, 400)
            b = parse_body(self)
            products = store.get("products", [])
            for prod in products:
                if prod["id"] == int(pid):
                    prod["name"] = b.get("name", prod["name"])
                    prod["title"] = (b.get("title", "") or "").strip()[:60]
                    prod["category"] = b.get("category", prod["category"])
                    prod["price"] = float(b.get("price", prod["price"]))
                    prod["stock"] = int(b.get("stock", prod["stock"]))
                    prod["image"] = b.get("image", prod["image"])
                    prod["detail_image"] = b.get("detail_image", prod.get("detail_image", ""))
                    prod["description"] = b.get("description", prod.get("description", ""))
                    prod["wechat"] = b.get("wechat", prod.get("wechat", ""))
                    prod["qq"] = b.get("qq", prod.get("qq", ""))
                    break
            store["products"] = products
            save_store(store)
            send_json(self, next((pr for pr in products if pr["id"] == int(pid)), {}))
        elif path == "/api/settings" and require_auth(self):
            b = parse_body(self)
            settings = store.get("settings", {})
            for k, v in b.items():
                settings[k] = str(v)
            store["settings"] = settings
            save_store(store)
            send_json(self, {"ok": True})
        elif path == "/api/admin/payment_qrcodes" and require_auth(self):
            b = parse_body(self)
            settings = store.get("settings", {})
            for k in ("wechat_pay_qr", "alipay_qr"):
                if k in b:
                    settings[k] = b[k]
            store["settings"] = settings
            save_store(store)
            send_json(self, {"ok": True})
        elif path == "/api/categories" and require_auth(self):
            b = parse_body(self)
            cats = b.get("categories", [])
            store["categories"] = cats
            save_store(store)
            send_json(self, {"ok": True})
        elif path == "/api/admin/order/confirm":
            if not require_auth(self):
                return send_json(self, {"error": "unauthorized"}, 401)
            b = parse_body(self)
            oid = b.get("order_id")
            if not oid:
                return send_json(self, {"error": "missing order_id"}, 400)
            orders = store.get("orders", [])
            # Support both old format (id) and new format (order_number)
            order = next((o for o in orders if o.get("order_number") == str(oid)), None)
            if not order:
                return send_json(self, {"error": "订单不存在"}, 404)
            products = store.get("products", [])
            for prod in products:
                if prod["id"] == order["product_id"]:
                    prod["stock"] = max(0, prod["stock"] - order["qty"])
                    break
            order["status"] = "completed"
            store["orders"] = orders
            store["products"] = products
            save_store(store)
            send_json(self, {"ok": True})
        else:
            self.send_error(404)

    def do_DELETE(self):
        p = urlparse(self.path)
        path = p.path.rstrip("/") or "/"
        qs = parse_qs(p.query)
        store = load_store()
        
        if path == "/api/categories":
            if not require_auth(self):
                return send_json(self, {"error": "unauthorized"}, 401)
            cid = qs.get("id", [None])[0]
            if not cid:
                return send_json(self, {"error": "missing id"}, 400)
            store["categories"] = [c for c in store.get("categories", []) if c["id"] != int(cid)]
            save_store(store)
            return send_json(self, {"ok": True})
        elif path == "/api/products":
            if not require_auth(self):
                return send_json(self, {"error": "unauthorized"}, 401)
            pid = qs.get("id", [None])[0]
            if not pid:
                return send_json(self, {"error": "missing id"}, 400)
            store["products"] = [pr for pr in store.get("products", []) if pr["id"] != int(pid)]
            save_store(store)
            send_json(self, {"ok": True})
        elif path == "/api/admin/order/clean":
            if not require_auth(self):
                return send_json(self, {"error": "unauthorized"}, 401)
            store = clean_expired(store)
            save_store(store)
            send_json(self, {"ok": True})
        elif path == "/api/admin/order/delete":
            if not require_auth(self):
                return send_json(self, {"error": "unauthorized"}, 401)
            oid = qs.get("id", [None])[0]
            if not oid:
                return send_json(self, {"error": "missing id"}, 400)
            store["orders"] = [o for o in store.get("orders", []) if o["id"] != int(oid)]
            save_store(store)
            send_json(self, {"ok": True})
        else:
            self.send_error(404)

    def serve(self, filepath, mime=None):
        if not os.path.isfile(filepath):
            return self.send_error(404)
        ext = os.path.splitext(filepath)[1].lower()
        mm = {".html":"text/html; charset=utf-8",".css":"text/css; charset=utf-8",
              ".js":"application/javascript; charset=utf-8",".json":"application/json",
              ".jpg":"image/jpeg",".png":"image/png",".gif":"image/gif",".webp":"image/webp"}
        mime = mime or mm.get(ext, "application/octet-stream")
        with open(filepath, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        try:
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionAbortedError):
            pass


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Startup diagnostics
    _vol = os.environ.get("RENDER_EXTERNAL_VOLUME", "").strip()
    if _vol and os.path.isdir(_vol):
        print("[V7] Using Render persistent volume: " + _vol, flush=True)
    else:
        print("[V7] Using local storage: " + DATA_DIR, flush=True)
    print("[V7] Data file: " + STORE_FILE, flush=True)
    print("[V7] Store exists: " + str(os.path.exists(STORE_FILE)), flush=True)
    # Always pull from git first
    ensure_git_remote()
    pull_data_from_git()
    
    # Load store data
    store = load_store()
    
    # Fallback: only use defaults on truly first run (no store file exists)
    if not os.path.exists(STORE_FILE):
        print("WARNING: No data found, using embedded defaults", flush=True)
        store = {
            "products": [
                {"id": 1, "name": "金渐层A", "title": "金渐层幼猫A窝", "category": "金渐层猫", "price": 2300.0, "stock": 5, "image": "placeholder.jpg", "detail_image": "", "description": "精品金渐层", "wechat": "", "qq": ""},
                {"id": 2, "name": "银渐层B", "title": "银渐层幼猫B窝", "category": "银渐层猫", "price": 2100.0, "stock": 3, "image": "placeholder.jpg", "detail_image": "", "description": "银渐层小猫", "wechat": "", "qq": ""},
                {"id": 3, "name": "宠物指甲剪", "title": "Miozaa宠物指甲剪猫狗通用保护血线", "category": "宠物用品", "price": 9.0, "stock": 18, "image": "placeholder.jpg", "detail_image": "", "description": "宠物指甲剪", "wechat": "", "qq": ""}
            ],
            "categories": [
                {"id": 1, "name": "全部", "sort_order": 0},
                {"id": 2, "name": "宠物用品", "sort_order": 1},
                {"id": 3, "name": "金渐层猫", "sort_order": 2},
                {"id": 4, "name": "银渐层猫", "sort_order": 3}
            ],
            "orders": [],
            "settings": {"site_title": "喵喵咪丫", "shop_description": "让每一只小猫咪找到温暖的家", "wechat_pay_qr": "", "alipay_qr": "", "wechat_qr": "", "shop_logo": ""},
            "admin": {"username": ADMIN_USER, "password": ADMIN_PASS}
        }
        save_store(store)
    
    # Ensure all expected keys exist
    store.setdefault("products", [])
    store.setdefault("categories", [])
    store.setdefault("orders", [])
    store.setdefault("settings", {"site_title": "喵喵咪丫", "shop_description": "", "wechat_pay_qr": "", "alipay_qr": "", "wechat_qr": "", "shop_logo": ""})
    store.setdefault("admin", {"username": ADMIN_USER, "password": ADMIN_PASS})
    
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), H)
    print(f"Pet shop running on http://0.0.0.0:{port}")
    print("Loaded " + str(len(store.get("products", []))) + " products, " + str(len(store.get("categories", []))) + " categories", flush=True)
    server.serve_forever()



if __name__ == "__main__":
    main()
