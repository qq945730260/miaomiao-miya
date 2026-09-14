import re, sys
sys.stdout.reconfigure(encoding='utf-8')
path = r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5\server.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

post_start = c.find('def do_POST')
put_start = c.find('def do_PUT')
delete_start = c.find('def do_DELETE')

post_body = c[post_start:put_start]
put_body = c[put_start:delete_start]

print("=== do_POST endpoints ===")
for m in re.finditer(r'elif path == "([^"]+)"', post_body):
    print("  ", m.group(1))

print("\n=== do_PUT endpoints ===")
for m in re.finditer(r'elif path == "([^"]+)"', put_body):
    print("  ", m.group(1))

print(f"\norder/confirm in POST: {'order/confirm' in post_body}")
print(f"order/confirm in PUT: {'order/confirm' in put_body}")
