"""Pet Shop Server V6 - Supabase via direct REST API (no SDK dependency)"""
import json, os, secrets, time, re, base64
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import urllib.request
import urllib.error

# ── Config ──────────────────────────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip()
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "").strip()
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
SUPABASE_BUCKET = os.environ.get("SUPABASE_STORAGE_BUCKET", "miaomiao-miya")
BLOCKED_DOMAIN = "miaomiao.au0817.dpdns.org"
ADMIN_PASS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".admin_pass")
SESSION_TTL = 86400
MAX_PRODUCTS = 30
ORDER_RETENTION_DAYS = 7

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")

def db_up():
    return bool(SUPABASE_URL and SUPABASE_ANON_KEY)

def api_get(table, columns="*", filters=None, order=None, limit=None):
    """GET from Supabase REST API."""
    if not db_up():
        return None
    url = f"{SUPABASE_URL}/rest/v1/{table}?select={columns}"
    if filters:
        for k, v in filters.items():
            url += f"&{k}=eq.{v}"
    if order:
        url += f"&order={order}"
    if limit:
        url += f"&limit={limit}"
    return _api_call("GET", url)

def api_insert(table, data):
    """INSERT into Supabase REST API."""
    if not db_up():
        return None
    url = f"{SUPABASE_URL}/rest/v1/{table}?select=*"
    return _api_call("POST", url, data)

def api_update(table, data, filters):
    """UPDATE Supabase REST API."""
    if not db_up():
        return None
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    for k, v in filters.items():
        url += f"&{k}=eq.{v}"
    return _api_call("PATCH", url, data)

def api_delete(table, filters):
    """DELETE from Supabase REST API."""
    if not db_up():
        return None
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    for k, v in filters.items():
        url += f"&{k}=eq.{v}"
    return _api_call("DELETE", url, None)

def _api_call(method, url, body=None):
    """Execute a Supabase REST API call."""
    try:
        req_data = json.dumps(body).encode("utf-8") if body else None
        headers = {
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation" if method in ("POST", "PATCH") else "",
        }
        if SUPABASE_SERVICE_KEY:
            headers["Authorization"] = f"Bearer {SUPABASE_SERVICE_KEY}"
            headers["apikey"] = SUPABASE_SERVICE_KEY
        req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status == 204:
                return {"ok": True}
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            err_text = e.read().decode("utf-8", errors="replace")
            print(f"HTTP Error {e.code}: {err_text[:300]}", flush=True)
            err_body = json.loads(err_text)
            return {"error": err_body.get("message", str(e))}
        except Exception as e2:
            print(f"HTTP Error parse failed: {e2}", flush=True)
            return {"error": str(e)}
    except Exception as e:
        print(f"API Error: {e}", flush=True)
        return {"error": str(e)}

def admin_password():
    env_pwd = os.environ.get("ADMIN_PASSWORD", "").strip()
    if env_pwd:
        return env_pwd
    if os.path.exists(ADMIN_PASS_FILE):
        with open(ADMIN_PASS_FILE, "r") as f:
            return f.read().strip()
    return "5361172"

def save_admin_password(pwd):
    with open(ADMIN_PASS_FILE, "w") as f:
        f.write(pwd)

def get_setting(key):
    result = api_get("settings", "value", {"key": key})
    if isinstance(result, list) and result:
        return result[0].get("value", "")
    return ""

def set_setting(key, value):
    existing = api_get("settings", "key", {"key": key})
    if isinstance(existing, list) and existing:
        return api_update("settings", {"key": key, "value": str(value)}, {"key": key})
    else:
        return api_insert("settings", {"key": key, "value": str(value)})

def get_settings_all():
    result = api_get("settings", "key,value")
    defaults = {
        "site_title": "喵喵咪丫", "shop_description": "",
        "wechat_pay_qr": "", "alipay_qr": "", "wechat_qr": "", "shop_logo": ""
    }
    if not isinstance(result, list):
        return defaults
    data = {row["key"]: row["value"] for row in result if isinstance(row, dict)}
    data.update(defaults)
    return data

def gen_order_number():
    date_str = time.strftime("%y%m%d")
    result = api_get("orders", "order_number")
    count = len(result) if isinstance(result, list) else 0
    # Count orders with same date prefix
    same_day = [o for o in (result or []) if isinstance(o, dict) and o.get("order_number","").startswith(date_str)]
    seq = len(same_day) + 1
    return date_str + str(seq).zfill(2)

def clean_expired_orders():
    if not db_up():
        return
    cutoff = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time() - ORDER_RETENTION_DAYS * 86400))
    api_delete("orders", {"created_at": f"lt.{cutoff}"})

def upload_image(file_bytes, filename):
    """Upload to Supabase Storage, return filename."""
    if not SUPABASE_SERVICE_KEY or not SUPABASE_URL:
        # Fallback to local
        ext = os.path.splitext(filename)[1].lower() or ".jpg"
        sn = secrets.token_hex(8) + ext
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        with open(os.path.join(UPLOAD_DIR, sn), "wb") as f:
            f.write(file_bytes)
        return sn
    try:
        ext = os.path.splitext(filename)[1].lower() or ".jpg"
        safe_name = secrets.token_hex(8) + ext
        # Use Supabase Storage v2 API with service role
        headers = {
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            "apikey": SUPABASE_SERVICE_KEY,
            "content-type": "application/octet-stream",
        }
        req = urllib.request.Request(
            f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{safe_name}",
            data=file_bytes.rstrip(b"\r\n"),
            headers=headers,
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                print(f"Storage upload status: {resp.status}", flush=True)
                return safe_name
        except urllib.error.HTTPError as he:
            err_body = he.read().decode("utf-8", errors="replace") if hasattr(he, "read") else ""
            print(f"Storage HTTP error {he.code}: {err_body[:200]}", flush=True)
        except Exception as e:
            print(f"Storage error: {e}", flush=True)
        # Fallback to local upload
        ext2 = os.path.splitext(filename)[1].lower() or ".jpg"
        sn = secrets.token_hex(8) + ext2
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        with open(os.path.join(UPLOAD_DIR, sn), "wb") as f:
            f.write(file_bytes.rstrip(b"\r\n"))
        print(f"Fallback: saved locally as {sn}", flush=True)
        return sn
    except Exception as e:
        print(f"Upload error: {e}", flush=True)
        ext = os.path.splitext(filename)[1].lower() or ".jpg"
        sn = secrets.token_hex(8) + ext
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        with open(os.path.join(UPLOAD_DIR, sn), "wb") as f:
            f.write(file_bytes.rstrip(b"\r\n"))
        return sn
        return sn


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def require_auth(self):
        for part in self.headers.get("Cookie", "").split(";"):
            part = part.strip()
            if part.startswith("session="):
                token = part[8:]
                fp = os.path.join(UPLOAD_DIR, "session_" + token)
                if os.path.exists(fp):
                    try:
                        if time.time() - os.path.getmtime(fp) < SESSION_TTL:
                            return True
                    except Exception:
                        pass
        return False

    def parse_body(self):
        n = int(self.headers.get("Content-Length", 0))
        if n == 0:
            return {}
        try:
            return json.loads(self.rfile.read(n))
        except Exception:
            return {}

    def serve_file(self, filepath, mime=None):
        if not os.path.isfile(filepath):
            return self.send_error(404)
        ext = os.path.splitext(filepath)[1].lower()
        mm = {".html":"text/html; charset=utf-8",".css":"text/css; charset=utf-8",
              ".js":"application/javascript; charset=utf-8",".json":"application/json",
              ".jpg":"image/jpeg",".png":"image/png",".gif":"image/gif",".webp":"image/webp",
              ".svg":"image/svg+xml"}
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

    def do_GET(self):
        p = urlparse(self.path)
        path = p.path.rstrip("/") or "/"
        qs = parse_qs(p.query)

        if path in ("/", "/index"):
            self.serve_file(os.path.join(STATIC_DIR, "index.html"), "text/html; charset=utf-8")
        elif path == "/product":
            self.serve_file(os.path.join(STATIC_DIR, "product.html"), "text/html; charset=utf-8")
        elif path == "/admin":
            host = self.headers.get("Host", "")
            if BLOCKED_DOMAIN and host == BLOCKED_DOMAIN:
                return self.send_json({"error": "forbidden"}, 403)
            self.serve_file(os.path.join(STATIC_DIR, "admin.html"), "text/html; charset=utf-8")
        elif path == "/api/products":
            result = api_get("products", "*", order="id")
            self.send_json(result if isinstance(result, list) else [])
        elif path == "/api/products" and "id" in qs:
            result = api_get("products", "*", {"id": qs["id"][0]})
            prod = result[0] if isinstance(result, list) and result else None
            if prod:
                self.send_json(prod)
            else:
                self.send_json({}, 404)
        elif path == "/api/settings":
            self.send_json(get_settings_all())
        elif path == "/api/admin/check":
            self.send_json({"auth": self.require_auth()})
        elif path == "/api/admin/test_login":
            # Debug endpoint - test login without DB call
            self.send_json({"ok": True, "debug": "CORS works"})
        elif path == "/api/admin/payment_qrcodes":
            if not self.require_auth():
                return self.send_json({"error": "unauthorized"}, 401)
            s = get_settings_all()
            self.send_json({"wechat_pay_qr": s.get("wechat_pay_qr",""), "alipay_qr": s.get("alipay_qr","")})
        elif path == "/api/categories":
            result = api_get("categories", "*", order="sort_order")
            self.send_json(result if isinstance(result, list) else [])
        elif path == "/api/orders":
            if not self.require_auth():
                return self.send_json({"error": "unauthorized"}, 401)
            clean_expired_orders()
            orders = api_get("orders", "*", order="created_at desc")
            products = {p["id"]: p for p in (api_get("products", "id,name,title,image") or [])}
            result = []
            for o in (orders or []):
                prod = products.get(o["product_id"], {})
                result.append({**o, "product_name": prod.get("name",""),
                               "product_title": prod.get("title",""),
                               "product_image": prod.get("image","")})
            self.send_json(result)
        elif path == "/api/sold":
            result = api_get("orders", "product_id,qty", {"status": "completed"})
            sold = {}
            for o in (result or []):
                pid = o.get("product_id")
                sold[pid] = sold.get(pid, 0) + o.get("qty", 1)
            self.send_json(sold)
        elif path == "/uploads":
            files = [f for f in os.listdir(UPLOAD_DIR) if not f.startswith(".") and not f.startswith("session_")] if os.path.exists(UPLOAD_DIR) else []
            self.send_json(files)
        elif path == "/api/debug":
            upload_count = len([f for f in os.listdir(UPLOAD_DIR) if not f.startswith(".") and not f.startswith("session_")]) if os.path.exists(UPLOAD_DIR) else 0
            test_result = api_get("settings", "key,value")
            db_ok = isinstance(test_result, list)
            db_error = test_result.get("error", "") if isinstance(test_result, dict) else ""
            prod_count = len(api_get("products", "id") or []) if db_ok else 0
            cat_count = len(api_get("categories", "id") or []) if db_ok else 0
            order_count = len(api_get("orders", "id") or []) if db_ok else 0
            self.send_json({
                "db_up": db_up(),
                "db_connected": db_ok,
                "db_error": db_error[:200],
                "upload_count": upload_count,
                "product_count": prod_count,
                "category_count": cat_count,
                "order_count": order_count,
                "supabase_url_set": bool(SUPABASE_URL),
                "supabase_key_set": bool(SUPABASE_ANON_KEY),
            })
        elif path.startswith("/static/"):
            self.serve_file(os.path.join(BASE_DIR, path.lstrip("/")))
        elif path.startswith("/uploads/"):
            filename = os.path.basename(path)
            local_path = os.path.join(UPLOAD_DIR, filename)
            if os.path.isfile(local_path):
                self.serve_file(local_path)
                return
            self.send_error(404)
        else:
            self.send_error(404)

    def do_POST(self):
        p = urlparse(self.path)
        path = p.path.rstrip("/") or "/"

        if path == "/api/admin/login":
            try:
                b = self.parse_body()
                username = b.get("username","").strip()
                password = b.get("password","").strip()
                print(f"LOGIN ATTEMPT: user={username!r} pwd_len={len(password)}", flush=True)
                stored_user = get_setting("admin_username") or "xuxu"
                stored_pwd = admin_password()
                print(f"STORED: user={stored_user!r} pwd_set={bool(stored_pwd)}", flush=True)
                if username == stored_user and password == stored_pwd:
                    tok = secrets.token_hex(16)
                    os.makedirs(UPLOAD_DIR, exist_ok=True)
                    open(os.path.join(UPLOAD_DIR, "session_" + tok), "w").close()
                    body = json.dumps({"ok": True}, ensure_ascii=False).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
                    self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
                    self.send_header("Set-Cookie", f"session={tok}; Path=/; Max-Age={SESSION_TTL}")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                    print("LOGIN SUCCESS", flush=True)
                else:
                    print(f"AUTH FAILED: user_match={username==stored_user} pwd_match={password==stored_pwd}", flush=True)
                    self.send_json({"error": "用户名或密码错误"}, 401)
            except Exception as e:
                print(f"LOGIN EXCEPTION: {e}", flush=True)
                try:
                    self.send_json({"error": "服务器内部错误: " + str(e)}, 500)
                except:
                    pass
        elif path == "/api/admin/change_password":
            if not self.require_auth():
                return self.send_json({"error": "unauthorized"}, 401)
            b = self.parse_body()
            old_pwd = b.get("old_password","")
            new_pwd = b.get("new_password","")
            if not old_pwd or not new_pwd:
                return self.send_json({"error": "missing fields"}, 400)
            if admin_password() == old_pwd:
                save_admin_password(new_pwd)
                return self.send_json({"ok": True})
            return self.send_json({"error": "old password wrong"}, 401)
        elif path == "/api/categories":
            if not self.require_auth():
                return self.send_json({"error": "unauthorized"}, 401)
            b = self.parse_body()
            name = b.get("name","").strip()
            if not name:
                return self.send_json({"error": "missing name"}, 400)
            all_cats = api_get("categories", "id")
            max_id = max([c["id"] for c in (all_cats or [])] or [0])
            next_id = max_id + 1
            rec = {"name": name, "sort_order": b.get("sort_order", 0), "id": next_id}
            result = api_insert("categories", rec)
            print(f"CATEGORY INSERT result: {result}", flush=True)
            if isinstance(result, list) and result:
                self.send_json({"id": result[0]["id"], "name": name, "sort_order": b.get("sort_order", 0)}, 201)
            elif isinstance(result, dict) and "error" in result:
                self.send_json({"error": result["error"]}, 500)
            else:
                self.send_json({"id": next_id, "name": name, "sort_order": b.get("sort_order", 0)}, 201)   elif path == "/api/products":
            if not self.require_auth():
                return self.send_json({"error": "unauthorized"}, 401)
            b = self.parse_body()
            # Check max
            all_prods = api_get("products", "id")
            if len(all_prods or []) >= MAX_PRODUCTS:
                return self.send_json({"error": f"商品数量已达上限 ({MAX_PRODUCTS})", "count": len(all_prods or [])}, 400)
            rec = {
                "name": b.get("name",""),
                "title": (b.get("title","") or "").strip()[:60],
                "category": b.get("category",""),
                "price": float(b.get("price", 0)),
                "stock": int(b.get("stock", 0)),
                "image": b.get("image",""),
                "detail_image": b.get("detail_image",""),
                "description": b.get("description",""),
                "wechat": b.get("wechat",""),
                "qq": b.get("qq",""),
            }
            result = api_insert("products", rec)
            if isinstance(result, list) and result:
                new_rec = result[0]
                new_rec["id"] = new_rec.get("id", 1)
                self.send_json(new_rec, 201)
            else:
                self.send_json({"error": str(result)}, 500)
        elif path == "/api/upload":
            if not self.require_auth():
                return self.send_json({"error": "unauthorized"}, 401)
            ct = self.headers.get("Content-Type","")
            m = re.search(r"boundary=(.+)", ct)
            if not m:
                return self.send_json({"error": "missing boundary"}, 400)
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
                    fn = os.path.basename(fm.group(1)).replace(" ","_")
                    ext = os.path.splitext(fn)[1].lower() or ".jpg"
                    if ext not in {".jpg",".jpeg",".png",".gif",".webp",".svg"}:
                        return self.send_json({"error": "bad ext"}, 400)
                    saved_name = upload_image(data, fn)
                    return self.send_json({"filename": saved_name})
            return self.send_json({"error": "no image"}, 400)
        elif path == "/api/order/create":
            b = self.parse_body()
            email = (b.get("email") or "").strip().lower()
            password = (b.get("password") or "").strip()
            product_id = b.get("product_id")
            qty = int(b.get("qty", 1))
            if not email or not password or product_id is None:
                return self.send_json({"error": "missing fields"}, 400)
            if not re.match(r"^[0-9]{6,8}$", password):
                return self.send_json({"error": "查询密码为6-8位数字"}, 400)
            prod_res = api_get("products", "*", {"id": str(product_id)})
            product = prod_res[0] if isinstance(prod_res, list) and prod_res else None
            if not product:
                return self.send_json({"error": "商品不存在"}, 404)
            total = round(float(product["price"]) * qty, 2)
            order_number = gen_order_number()
            now = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            order_rec = {
                "order_number": order_number,
                "email": email,
                "password": password,
                "product_id": int(product_id),
                "qty": qty,
                "total": total,
                "status": "pending",
                "created_at": now,
            }
            result = api_insert("orders", order_rec)
            if isinstance(result, list) and result:
                new_order = result[0]
                self.send_json({
                    "ok": True,
                    "order_id": new_order.get("order_number", order_number),
                    "order_number": new_order.get("order_number", order_number),
                    "total": total,
                    "product_name": product["name"],
                })
            else:
                self.send_json({"error": str(result)}, 500)
        elif path == "/api/order/query":
            b = self.parse_body()
            email = (b.get("email") or "").strip().lower()
            password = (b.get("password") or "").strip()
            if not email or not password:
                return self.send_json({"error": "missing fields"}, 400)
            clean_expired_orders()
            result = api_get("orders", "*", {"email": email, "password": password})
            order = result[0] if isinstance(result, list) and result else None
            if order:
                result_no_status = {k: v for k, v in order.items() if k != "status"}
                prod_res = api_get("products", "name", {"id": str(order["product_id"])})
                if prod_res:
                    result_no_status["product_name"] = prod_res[0].get("name","")
                self.send_json(result_no_status)
            else:
                self.send_json({"error": "未找到订单，请确认邮箱和密码是否正确"}, 404)
        elif path == "/api/order/confirm":
            b = self.parse_body()
            oid = b.get("order_id")
            if not oid:
                return self.send_json({"error": "missing order_id"}, 400)
            result = api_get("orders", "*", {"order_number": str(oid)})
            order = result[0] if isinstance(result, list) and result else None
            if not order:
                return self.send_json({"error": "订单不存在"}, 404)
            if order.get("status") == "completed":
                return self.send_json({"ok": True, "already": True})
            # Decrease stock
            prod_res = api_get("products", "stock", {"id": str(order["product_id"])})
            if prod_res:
                current_stock = prod_res[0].get("stock", 0)
                new_stock = max(0, current_stock - order["qty"])
                api_update("products", {"stock": new_stock}, {"id": str(order["product_id"])})
            api_update("orders", {"status": "completed"}, {"order_number": str(oid)})
            return self.send_json({"ok": True})
        else:
            self.send_error(404)

    def do_PUT(self):
        p = urlparse(self.path)
        path = p.path.rstrip("/") or "/"
        qs = parse_qs(p.query)

        if path == "/api/products" and self.require_auth():
            pid = qs.get("id", [None])[0]
            if not pid:
                return self.send_json({"error": "missing id"}, 400)
            b = self.parse_body()
            rec = {
                "name": b.get("name",""),
                "title": (b.get("title","") or "").strip()[:60],
                "category": b.get("category",""),
                "price": float(b.get("price", 0)),
                "stock": int(b.get("stock", 0)),
                "image": b.get("image",""),
                "detail_image": b.get("detail_image",""),
                "description": b.get("description",""),
                "wechat": b.get("wechat",""),
                "qq": b.get("qq",""),
            }
            result = api_update("products", rec, {"id": pid})
            if isinstance(result, list) and result:
                result[0]["id"] = int(pid)
                self.send_json(result[0])
            else:
                self.send_json({"error": str(result)}, 500)
        elif path == "/api/settings" and self.require_auth():
            b = self.parse_body()
            for k, v in b.items():
                set_setting(k, v)
            self.send_json({"ok": True})
        elif path == "/api/admin/payment_qrcodes" and self.require_auth():
            b = self.parse_body()
            for k in ("wechat_pay_qr", "alipay_qr"):
                if k in b:
                    set_setting(k, b[k])
            self.send_json({"ok": True})
        elif path == "/api/categories" and self.require_auth():
            b = self.parse_body()
            cats = b.get("categories", [])
            for c in cats:
                api_update("categories", {"name": c.get("name",""), "sort_order": c.get("sort_order", 0)}, {"id": str(c["id"])})
            self.send_json({"ok": True})
        elif path == "/api/admin/order/confirm" and self.require_auth():
            b = self.parse_body()
            oid = b.get("order_id")
            if not oid:
                return self.send_json({"error": "missing order_id"}, 400)
            result = api_get("orders", "*", {"order_number": str(oid)})
            order = result[0] if isinstance(result, list) and result else None
            if not order:
                return self.send_json({"error": "订单不存在"}, 404)
            if order.get("status") == "completed":
                return self.send_json({"ok": True, "already": True})
            prod_res = api_get("products", "stock", {"id": str(order["product_id"])})
            if prod_res:
                new_stock = max(0, prod_res[0].get("stock", 0) - order["qty"])
                api_update("products", {"stock": new_stock}, {"id": str(order["product_id"])})
            api_update("orders", {"status": "completed"}, {"order_number": str(oid)})
            return self.send_json({"ok": True})
        else:
            self.send_error(404)

    def do_DELETE(self):
        p = urlparse(self.path)
        path = p.path.rstrip("/") or "/"
        qs = parse_qs(p.query)

        if path == "/api/categories":
            if not self.require_auth():
                return self.send_json({"error": "unauthorized"}, 401)
            cid = qs.get("id", [None])[0]
            if cid:
                api_delete("categories", {"id": cid})
            return self.send_json({"ok": True})
        elif path == "/api/products":
            if not self.require_auth():
                return self.send_json({"error": "unauthorized"}, 401)
            pid = qs.get("id", [None])[0]
            if pid:
                api_delete("products", {"id": pid})
            return self.send_json({"ok": True})
        elif path == "/api/admin/order/clean":
            if not self.require_auth():
                return self.send_json({"error": "unauthorized"}, 401)
            clean_expired_orders()
            return self.send_json({"ok": True})
        elif path == "/api/admin/order/delete":
            if not self.require_auth():
                return self.send_json({"error": "unauthorized"}, 401)
            oid = qs.get("id", [None])[0]
            if oid:
                api_delete("orders", {"id": oid})
            return self.send_json({"ok": True})
        else:
            self.send_error(404)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    if not os.path.exists(ADMIN_PASS_FILE):
        save_admin_password(admin_password())

    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), H)
    print(f"Pet shop V6 (Supabase) running on http://0.0.0.0:{port}", flush=True)
    print(f"Supabase connected: {db_up()}", flush=True)
    server.serve_forever()

if __name__ == "__main__":
    main()
