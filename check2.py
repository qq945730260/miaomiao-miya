import re, sys
sys.stdout.reconfigure(encoding='utf-8')
path = r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5\server.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Find which do_ methods contain order endpoints
for m in re.finditer(r'def (do_\w+)\(self\):(.*?)(?=def do_\w+\(self\)|$)', c, re.DOTALL):
    method = m.group(1)
    body = m.group(2)
    endpoints = []
    if '/api/order/confirm' in body: endpoints.append('confirm')
    if '/api/order/create' in body: endpoints.append('create')
    if '/api/order/query' in body: endpoints.append('query')
    if endpoints:
        print(f'{method}: {", ".join(endpoints)}')

# Show lines around order/confirm in PUT
idx_put = c.find('def do_PUT')
idx_delete = c.find('def do_DELETE')
if idx_put >= 0:
    snippet = c[idx_put:idx_delete]
    confirm_idx = snippet.find('/api/order/confirm')
    if confirm_idx >= 0:
        print('\norder/confirm is in do_PUT (lines ~436-457)')
        # show context
        lines = snippet[confirm_idx-100:confirm_idx+300].split('\n')
        for l in lines[:15]:
            print('  ', l[:100])
