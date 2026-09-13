"""Pet Shop Server V4"""
import json, os, secrets, sqlite3, time, re, subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
STATIC_DIR = os.path.join(BASE_DIR, "static")
DB_PATH = os.path.join(DATA_DIR, "products.db")
ADMIN_USER = "xuxu"
ADMIN_PASS = "5361172"
SESSION_TTL = 86400
MAX_PRODUCTS = 30
BLOCKED_DOMAIN = "miaomiao.au0817.dpdns.org"
ORDER_RETENTION_DAYS = 7


def get_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        title TEXT DEFAULT '',
        category TEXT NOT NULL,
        price REAL NOT NULL,
        stock INTEGER NOT NULL DEFAULT 0,
        image TEXT DEFAULT 'placeholder.jpg',
        detail_image TEXT DEFAULT '',
        description TEXT DEFAULT '',
        wechat TEXT DEFAULT '',
        qq TEXT DEFAULT '')""")
    c.execute("""CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        sort_order INTEGER NOT NULL DEFAULT 0)""")
    c.execute("""CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        password TEXT NOT NULL,
        product_id INTEGER NOT NULL,
        qty INTEGER NOT NULL,
        total REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        created_at TEXT NOT NULL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL DEFAULT '')""")
    c.execute("CREATE TABLE IF NOT EXISTS admin (username TEXT PRIMARY KEY, password TEXT)")
    for k, v in [("site_title","喵喵咪丫"),("shop_description",""),
                  ("wechat_pay_qr",""),("alipay_qr",""),("wechat_qr",""),
                  ("shop_logo","")]:
        c.execute("INSERT OR IGNORE INTO settings VALUES (?,?)", (k, v))
    if c.execute("SELECT COUNT(*) FROM admin").fetchone()[0] == 0:
        c.execute("INSERT INTO admin VALUES (?,?)", (ADMIN_USER, ADMIN_PASS))
    if c.execute("SELECT COUNT(*) FROM categories").fetchone()[0] == 0:
        for name, order in [("萌宠", 0), ("宠物用品", 1), ("其它", 2)]:
            c.execute("INSERT INTO categories(name, sort_order) VALUES (?,?)", (name, order))
    try:
        conn.execute("ALTER TABLE products ADD COLUMN detail_image TEXT DEFAULT ''")
        conn.commit()
    except Exception:
        pass
    try:
        conn.execute("ALTER TABLE products ADD COLUMN title TEXT DEFAULT ''")
        conn.commit()
    except Exception:
        pass
    conn.close()


def send_json(h, data, status=200):
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    h.send_response(status)
    h.send_header("Content-Type", "application/json; charset=utf-8")
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


SYNC_LOG = os.path.join(BASE_DIR, "data", "sync.log")

def log_sync(msg):
    try:
        os.makedirs(os.path.dirname(SYNC_LOG), exist_ok=True)
        with open(SYNC_LOG, "a", encoding="utf-8") as f:
            f.write(time.strftime("%Y-%m-%d %H:%M:%S") + " " + msg + "\n")
    except Exception:
        pass

def do_commit(force=False):
    """Commit and push data/uploads to git."""
    token = os.environ.get('GH_TOKEN', '').strip()
    if not token:
        log_sync('SKIP: GH_TOKEN not set')
        return {"ok": False, "error": "GH_TOKEN未配置"}
    try:
        r = subprocess.run(['git', '-c', 'safe.directory=*', 'add', '-A', 'data/', 'uploads/'],
            capture_output=True, timeout=10, cwd=BASE_DIR)
        r2 = subprocess.run(['git', '-c', 'safe.directory=*', 'commit', '-q', '--allow-empty', '-m', 'auto-commit data'],
            capture_output=True, timeout=10, cwd=BASE_DIR)
        changed = b'nothing' not in r2.stdout and b'nothing' not in r2.stderr
        if not changed and not force:
            log_sync('SKIP: no changes')
            return {"ok": True, "message": "no_changes"}
        if changed or force:
            r3 = subprocess.run(['git', '-c', 'safe.directory=*',
                'push', 'https://'+token+'@github.com/qq945730260/miaomiao-miya.git', 'main'],
                capture_output=True, timeout=30, cwd=BASE_DIR)
            if r3.returncode == 0:
                log_sync('OK: pushed')
                return {"ok": True, "message": "已同步"}
            else:
                err = r3.stderr.decode("utf-8", errors="replace")[:300]
                log_sync('FAIL: ' + err)
                return {"ok": False, "error": err}
    except Exception as e:
        log_sync('EXC: ' + str(e))
        return {"ok": False, "error": str(e)}

def auto_commit():
    return do_commit()

def clean_expired(conn):
    cutoff = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time() - ORDER_RETENTION_DAYS * 86400))
    conn.execute("DELETE FROM orders WHERE created_at < ?", (cutoff,))
    conn.commit()


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        p = urlparse(self.path)
        path = p.path.rstrip("/") or "/"
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
            conn = get_db()
            if "id" in qs:
                row = conn.execute("SELECT * FROM products WHERE id=?", (int(qs["id"][0]),)).fetchone()
                conn.close()
                send_json(self, dict(row) if row else {}, 404 if not row else 200)
            else:
                rows = conn.execute(
                    "SELECT * FROM products ORDER BY CASE WHEN category IN ('金渐层幼猫','金渐层大猫','银渐层幼猫','银渐层大猫') THEN 0 ELSE 1 END, id ASC").fetchall()
                conn.close()
                send_json(self, [dict(r) for r in rows])
        elif path == "/api/settings":
            conn = get_db()
            rows = conn.execute("SELECT key, value FROM settings").fetchall()
            conn.close()
            send_json(self, {r[0]: r[1] for r in rows})
        elif path == "/api/admin/check":
            send_json(self, {"auth": require_auth(self)})
        elif path == "/api/admin/payment_qrcodes":
            if not require_auth(self):
                return send_json(self, {"error": "unauthorized"}, 401)
            conn = get_db()
            rows = conn.execute("SELECT key, value FROM settings WHERE key IN ('wechat_pay_qr','alipay_qr')").fetchall()
            conn.close()
            send_json(self, {r[0]: r[1] for r in rows})
        elif path == "/api/categories":
            conn = get_db()
            rows = conn.execute("SELECT id, name, sort_order FROM categories ORDER BY sort_order ASC").fetchall()
            conn.close()
            send_json(self, [{"id": r[0], "name": r[1], "sort_order": r[2]} for r in rows])
        elif path == "/api/orders":
            if not require_auth(self):
                return send_json(self, {"error": "unauthorized"}, 401)
            conn = get_db()
            clean_expired(conn)
            rows = conn.execute(
                "SELECT o.*, p.name as product_name, p.title as product_title, p.image as product_image "
                "FROM orders o LEFT JOIN products p ON o.product_id = p.id ORDER BY o.created_at DESC").fetchall()
            conn.close()
            send_json(self, [dict(r) for r in rows])
        elif path == "/uploads":
            send_json(self, os.listdir(UPLOAD_DIR) if os.path.exists(UPLOAD_DIR) else [])
        elif path == "/api/debug":
            db_path = os.path.join(BASE_DIR, "data", "products.db")
            db_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0
            upload_dir = os.path.join(BASE_DIR, "uploads")
            upload_count = len([f for f in os.listdir(upload_dir) if f != ".gitkeep"]) if os.path.exists(upload_dir) else 0
            conn = get_db()
            prod_count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
            cat_count = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
            order_count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
            conn.close()
            sync_log_exists = os.path.exists(SYNC_LOG)
            sync_log = ""
            if sync_log_exists:
                with open(SYNC_LOG, "r", encoding="utf-8") as f:
                    sync_log = f.read()[-1500:]
            send_json(self, {
                "db_size": db_size,
                "upload_count": upload_count,
                "product_count": prod_count,
                "category_count": cat_count,
                "order_count": order_count,
                "gh_token_set": bool(os.environ.get("GH_TOKEN", "").strip()),
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
        if path == "/api/admin/login":
            b = parse_body(self)
            if b.get("username") == ADMIN_USER and b.get("password") == ADMIN_PASS:
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
            old_pwd = b.get("old_password", "")
            new_pwd = b.get("new_password", "")
            if not old_pwd or not new_pwd:
                return send_json(self, {"error": "missing fields"}, 400)
            conn = get_db()
            row = conn.execute("SELECT password FROM admin WHERE username=?", (ADMIN_USER,)).fetchone()
            conn.close()
            if row and row[0] == old_pwd:
                conn2 = get_db()
                conn2.execute("UPDATE admin SET password=?", (new_pwd,))
                conn2.commit()
                conn2.close()
                return send_json(self, {"ok": True})
            return send_json(self, {"error": "old password wrong"}, 401)
        elif path == "/api/categories" and require_auth(self):
            b = parse_body(self)
            name = b.get("name", "").strip()
            if not name:
                return send_json(self, {"error": "missing name"}, 400)
            conn = get_db()
            c = conn.cursor()
            c.execute("INSERT INTO categories(name, sort_order) VALUES (?,?)",
                      (name, int(b.get("sort_order", 0))))
            conn.commit()
            row = conn.execute(
                "SELECT id, name, sort_order FROM categories WHERE id=?",
                (c.lastrowid,)).fetchone()
            conn.close()
            send_json(self, {"id": row[0], "name": row[1], "sort_order": row[2]} if row else {}, 201)
        elif path == "/api/products":
            if not require_auth(self):
                return send_json(self, {"error": "unauthorized"}, 401)
            conn = get_db()
            count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
            if count >= MAX_PRODUCTS:
                conn.close()
                return send_json(self, {"error": "商品数量已达上限 (" + str(MAX_PRODUCTS) + ")", "count": count}, 400)
            b = parse_body(self)
            title = (b.get("title", "") or "").strip()[:60]
            c = conn.cursor()
            c.execute(
                "INSERT INTO products(name,title,category,price,stock,image,detail_image,description,wechat,qq) VALUES(?,?,?,?,?,?,?,?,?,?)",
                (b.get("name",""), title, b.get("category",""), float(b.get("price",0)),
                 int(b.get("stock",0)), b.get("image","placeholder.jpg"), b.get("detail_image",""),
                 b.get("description",""), b.get("wechat",""), b.get("qq","")))
            conn.commit()
            pid = c.lastrowid
            row = conn.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
            conn.close()
            send_json(self, dict(row) if row else {}, 201)
        elif path == "/api/admin/sync":
            if not require_auth(self):
                return send_json(self, {"error": "unauthorized"}, 401)
            result = do_commit(force=True)
            send_json(self, result)
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
                    return send_json(self, {"filename": sn})
            send_json(self, {"error": "no image"}, 400)
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
            conn = get_db()
            product = conn.execute("SELECT * FROM products WHERE id=?", (int(product_id),)).fetchone()
            if not product:
                conn.close()
                return send_json(self, {"error": "商品不存在"}, 404)
            total = round(float(product["price"]) * qty, 2)
            now = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            c = conn.cursor()
            c.execute("INSERT INTO orders(email,password,product_id,qty,total,status,created_at) VALUES(?,?,?,?,?,?,?)",
                      (email, password, int(product_id), qty, total, "pending", now))
            conn.commit()
            oid = c.lastrowid
            conn.close()
            send_json(self, {"ok": True, "order_id": oid, "total": total, "product_name": product["name"]})
        elif path == "/api/order/query":
            b = parse_body(self)
            email = (b.get("email") or "").strip().lower()
            password = (b.get("password") or "").strip()
            if not email or not password:
                return send_json(self, {"error": "missing fields"}, 400)
            conn = get_db()
            clean_expired(conn)
            row = conn.execute(
                "SELECT * FROM orders WHERE email=? AND password=? AND status='pending' ORDER BY created_at DESC LIMIT 1",
                (email, password)).fetchone()
            conn.close()
            if row:
                send_json(self, dict(row))
            else:
                send_json(self, {"error": "未找到订单，请确认邮箱和密码是否正确"}, 404)
        else:
            self.send_error(404)

    def do_PUT(self):
        p = urlparse(self.path)
        path = p.path.rstrip("/") or "/"
        qs = parse_qs(p.query)
        if path == "/api/products" and require_auth(self):
            pid = qs.get("id", [None])[0]
            if not pid:
                return send_json(self, {"error": "missing id"}, 400)
            b = parse_body(self)
            title = (b.get("title", "") or "").strip()[:60]
            conn = get_db()
            conn.execute(
                "UPDATE products SET name=?,title=?,category=?,price=?,stock=?,image=?,detail_image=?,description=?,wechat=?,qq=? WHERE id=?",
                (b.get("name",""), title, b.get("category",""), float(b.get("price",0)),
                 int(b.get("stock",0)), b.get("image","placeholder.jpg"), b.get("detail_image",""),
                 b.get("description",""), b.get("wechat",""), b.get("qq",""), int(pid)))
            conn.commit()
            row = conn.execute("SELECT * FROM products WHERE id=?", (int(pid),)).fetchone()
            conn.close()
            send_json(self, dict(row) if row else {})
        elif path == "/api/settings" and require_auth(self):
            b = parse_body(self)
            conn = get_db()
            for k, v in b.items():
                conn.execute("INSERT OR REPLACE INTO settings VALUES (?,?)", (k, str(v)))
            conn.commit()
            conn.close()
            send_json(self, {"ok": True})
        elif path == "/api/admin/payment_qrcodes" and require_auth(self):
            b = parse_body(self)
            conn = get_db()
            for k in ("wechat_pay_qr", "alipay_qr"):
                v = b.get(k, "")
                conn.execute("INSERT OR REPLACE INTO settings VALUES (?,?)", (k, str(v)))
            conn.commit()
            conn.close()
            send_json(self, {"ok": True})
        elif path == "/api/categories" and require_auth(self):
            b = parse_body(self)
            cats = b.get("categories", [])
            conn = get_db()
            for item in cats:
                cid = item.get("id")
                name = item.get("name", "").strip()
                order = int(item.get("sort_order", 0))
                if cid and name:
                    conn.execute("UPDATE categories SET name=?, sort_order=? WHERE id=?", (name, order, int(cid)))
            conn.commit()
            conn.close()
            send_json(self, {"ok": True})
        elif path == "/api/order/confirm":
            b = parse_body(self)
            oid = b.get("order_id")
            if not oid:
                return send_json(self, {"error": "missing order_id"}, 400)
            conn = get_db()
            order = conn.execute("SELECT * FROM orders WHERE id=?", (int(oid),)).fetchone()
            if not order:
                conn.close()
                return send_json(self, {"error": "订单不存在"}, 404)
            if order["status"] == "completed":
                conn.close()
                return send_json(self, {"ok": True, "already": True})
            conn.execute("UPDATE products SET stock=stock-? WHERE id=? AND stock>=?",
                         (order["qty"], order["product_id"], order["qty"]))
            conn.execute("UPDATE orders SET status='completed' WHERE id=?", (int(oid),))
            conn.commit()
            conn.close()
            send_json(self, {"ok": True})
        elif path == "/api/admin/order/confirm":
            if not require_auth(self):
                return send_json(self, {"error": "unauthorized"}, 401)
            b = parse_body(self)
            oid = b.get("order_id")
            if not oid:
                return send_json(self, {"error": "missing order_id"}, 400)
            conn = get_db()
            order = conn.execute("SELECT * FROM orders WHERE id=?", (int(oid),)).fetchone()
            if not order:
                conn.close()
                return send_json(self, {"error": "订单不存在"}, 404)
            conn.execute("UPDATE products SET stock=stock-? WHERE id=? AND stock>=?",
                         (order["qty"], order["product_id"], order["qty"]))
            conn.execute("UPDATE orders SET status='completed' WHERE id=?", (int(oid),))
            conn.commit()
            conn.close()
            send_json(self, {"ok": True})
        else:
            self.send_error(404)

    def do_DELETE(self):
        p = urlparse(self.path)
        path = p.path.rstrip("/") or "/"
        qs = parse_qs(p.query)
        if path == "/api/categories":
            if not require_auth(self):
                return send_json(self, {"error": "unauthorized"}, 401)
            cid = qs.get("id", [None])[0]
            if not cid:
                return send_json(self, {"error": "missing id"}, 400)
            conn = get_db()
            conn.execute("DELETE FROM categories WHERE id=?", (int(cid),))
            conn.commit()
            conn.close()
            return send_json(self, {"ok": True})
        elif path == "/api/products":
            if not require_auth(self):
                return send_json(self, {"error": "unauthorized"}, 401)
            pid = qs.get("id", [None])[0]
            if not pid:
                return send_json(self, {"error": "missing id"}, 400)
            conn = get_db()
            conn.execute("DELETE FROM products WHERE id=?", (int(pid),))
            conn.commit()
            conn.close()
            send_json(self, {"ok": True})
        elif path == "/api/admin/order/clean":
            if not require_auth(self):
                return send_json(self, {"error": "unauthorized"}, 401)
            conn = get_db()
            clean_expired(conn)
            conn.close()
            send_json(self, {"ok": True})
        elif path == "/api/admin/order/delete":
            if not require_auth(self):
                return send_json(self, {"error": "unauthorized"}, 401)
            oid = qs.get("id", [None])[0]
            if not oid:
                return send_json(self, {"error": "missing id"}, 400)
            conn = get_db()
            conn.execute("DELETE FROM orders WHERE id=?", (int(oid),))
            conn.commit()
            conn.close()
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
    init_db()
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), H)
    print(f"Pet shop running on http://0.0.0.0:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
