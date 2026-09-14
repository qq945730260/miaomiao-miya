import sys, re
sys.stdout.reconfigure(encoding='utf-8')
path = r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5\server.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Find which method handlers contain /api/order/confirm
for match in re.finditer(r'def (do_\w+)\(self\):(.*?)(?=def do_\w+\(self\)|$)', c, re.DOTALL):
    method = match.group(1)
    body = match.group(2)
    if '/api/order/confirm' in body:
        print(f'FOUND /api/order/confirm in {method}')
        # Show context
        idx = body.find('/api/order/confirm')
        print('  context:', body[max(0,idx-30):idx+80])

print()
# Also check if /api/order/create is in POST or PUT
for match in re.finditer(r'def (do_\w+)\(self\):(.*?)(?=def do_\w+\(self\)|$)', c, re.DOTALL):
    method = match.group(1)
    body = match.group(2)
    if '/api/order/create' in body:
        print(f'FOUND /api/order/create in {method}')
    if '/api/order/query' in body:
        print(f'FOUND /api/order/query in {method}')
