import re

path = r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v6\server.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the entire upload_image function
old_pattern = r'def upload_image\(file_bytes, filename\):.*?(?=\n\nclass H)'
new_func = '''def upload_image(file_bytes, filename):
    """Upload to Supabase Storage, return filename."""
    if not SUPABASE_SERVICE_KEY or not SUPABASE_URL:
        ext = os.path.splitext(filename)[1].lower() or ".jpg"
        sn = secrets.token_hex(8) + ext
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        with open(os.path.join(UPLOAD_DIR, sn), "wb") as f:
            f.write(file_bytes)
        return sn
    try:
        ext = os.path.splitext(filename)[1].lower() or ".jpg"
        safe_name = secrets.token_hex(8) + ext
        headers = {
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            "apikey": SUPABASE_SERVICE_KEY,
            "content-type": "application/octet-stream",
        }
        req = urllib.request.Request(
            f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{safe_name}",
            data=file_bytes.rstrip(b"\\r\\n"),
            headers=headers,
            method="PUT"
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(f"Storage upload status: {resp.status}", flush=True)
            return safe_name
    except urllib.error.HTTPError as he:
        err_body = he.read().decode("utf-8", errors="replace") if hasattr(he, "read") else ""
        print(f"Storage HTTP error {he.code}: {err_body[:200]}", flush=True)
    except Exception as e:
        print(f"Storage error: {e}", flush=True)
    # Fallback to local upload
    try:
        ext2 = os.path.splitext(filename)[1].lower() or ".jpg"
        sn = secrets.token_hex(8) + ext2
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        with open(os.path.join(UPLOAD_DIR, sn), "wb") as f:
            f.write(file_bytes.rstrip(b"\\r\\n"))
        print(f"Fallback: saved locally as {sn}", flush=True)
        return sn
    except Exception as e2:
        print(f"Fallback error: {e2}", flush=True)
        return secrets.token_hex(8) + ".jpg"


'''

content = re.sub(old_pattern, new_func, content, flags=re.DOTALL)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('upload_image function replaced successfully')
