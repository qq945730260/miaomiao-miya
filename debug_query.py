import json, sys, re
sys.stdout.reconfigure(encoding='utf-8')

# Check store.json
with open(r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5\data\store.json', encoding='utf-8') as f:
    d = json.load(f)
print('=== orders ===')
for o in d.get('orders', []):
    print(f"  num={o.get('order_number')} email={o.get('email')} status={o.get('status')} created={o.get('created_at')}")

# Check main.js query order function
with open(r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5\static\js\main.js', encoding='utf-8') as f:
    js = f.read()

# Find doQueryOrder
idx = js.find('doQueryOrder')
if idx < 0:
    idx = js.find('queryOrder')
print(f'\n=== doQueryOrder at index {idx} ===')
print(js[idx:idx+600])

# Check product.html for order query
with open(r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5\static\index.html', encoding='utf-8') as f:
    html = f.read()
idx2 = html.find('查询订单')
print(f'\n=== index.html query section at {idx2} ===')
print(html[max(0,idx2-50):idx2+300])
