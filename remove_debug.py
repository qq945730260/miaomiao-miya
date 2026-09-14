import sys
sys.stdout.reconfigure(encoding='utf-8')
path = r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5\server.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Remove the debug logging added earlier
old_debug = '''            import re as _re
            matches = [o for o in orders if o.get("email") == email and o.get("password") == password]
            print(f"QUERY: email={email} pwd={password!r} total_orders={len(orders)} matches={len(matches)}", flush=True)
            for mo in matches:
                print(f"  MATCH: num={mo.get('order_number')} email={mo.get('email')} pwd={mo.get('password')!r} status={mo.get('status')}", flush=True)
            order = matches[0] if matches else None'''

new_clean = '''            order = next((o for o in orders if o.get("email") == email and o.get("password") == password), None)'''

if old_debug in c:
    c = c.replace(old_debug, new_clean, 1)
    print("Removed debug logging")
else:
    print("Debug logging not found, checking...")
    if 'print(f"QUERY:' in c:
        print("Found partial debug, searching for exact match...")
        idx = c.find('import re as _re')
        print(repr(c[idx:idx+400]))
    else:
        print("No debug found")

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

# Verify
with open(path, 'r', encoding='utf-8') as f:
    c2 = f.read()
print("debug removed:", 'print(f"QUERY:' not in c2)
print("clean query:", 'next((o for o in orders' in c2)
