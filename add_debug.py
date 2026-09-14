import sys, json
sys.stdout.reconfigure(encoding='utf-8')

# Add debug logging to /api/order/query endpoint in server.py
path = r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5\server.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Find the query handler and add debug log
old_query_logic = '''            order = next((o for o in orders if o.get("email") == email and o.get("password") == password), None)
            if order:'''

new_query_logic = '''            import re as _re
            matches = [o for o in orders if o.get("email") == email and o.get("password") == password]
            print(f"QUERY: email={email} pwd={password!r} total_orders={len(orders)} matches={len(matches)}", flush=True)
            for mo in matches:
                print(f"  MATCH: num={mo.get('order_number')} email={mo.get('email')} pwd={mo.get('password')!r} status={mo.get('status')}", flush=True)
            order = matches[0] if matches else None
            if order:'''

if old_query_logic in c:
    c = c.replace(old_query_logic, new_query_logic, 1)
    print("Added debug logging to order/query")
else:
    print("WARNING: query logic pattern not found, searching...")
    # Find and show context
    idx = c.find('o.get("email") == email and o.get("password") == password')
    if idx >= 0:
        print("Found at", idx)
        print(repr(c[idx-50:idx+200]))
    else:
        print("NOT FOUND at all")

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

print("Server.py updated with debug logging")
