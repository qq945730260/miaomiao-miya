import sys, json, re
sys.stdout.reconfigure(encoding='utf-8')

# Check store.json orders
with open(r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5\data\store.json', encoding='utf-8') as f:
    d = json.load(f)
print("=== store.json orders ===")
for o in d.get('orders', []):
    print(f"  num={o.get('order_number')} email={o.get('email')} pwd={o.get('password')} pid={o.get('product_id')} qty={o.get('qty')} status={o.get('status')} created={o.get('created_at')}")

print()
print("=== server.py order/query endpoint ===")
with open(r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5\server.py', encoding='utf-8') as f:
    sc = f.read()
idx = sc.find('/api/order/query')
print(sc[idx:idx+500])

print()
print("=== main.js doQueryOrder ===")
with open(r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5\static\js\main.js', encoding='utf-8') as f:
    js = f.read()
idx2 = js.find('doQueryOrder()')
print(js[idx2:idx2+600])

print()
print("=== main.js loadOrders ===")
idx3 = js.find('function loadOrders')
print(js[idx3:idx3+500])

print()
print("=== main.js buildCard stock line ===")
idx4 = js.find('已售')
print(js[max(0,idx4-100):idx4+100])
