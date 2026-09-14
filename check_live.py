import sys, json, urllib.request
sys.stdout.reconfigure(encoding='utf-8')
try:
    r = urllib.request.urlopen('https://miaomiao-miya.onrender.com/api/debug', timeout=10)
    d = json.loads(r.read())
    print("debug:", json.dumps(d, indent=2, ensure_ascii=False))
except Exception as e:
    print("error:", e)
