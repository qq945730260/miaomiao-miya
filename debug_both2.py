import sys, json, re
sys.stdout.reconfigure(encoding='utf-8')

# Check server.py order/query - find full handler
with open(r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5\server.py', encoding='utf-8') as f:
    sc = f.read()
idx = sc.find('/api/order/query')
print("=== order/query handler ===")
print(sc[idx:idx+600])

print()
# Check if /api/orders returns status field
idx2 = sc.find('/api/orders"')
print("=== /api/orders handler ===")
print(sc[idx2:idx2+400])

# Check store.json orders
with open(r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5\data\store.json', encoding='utf-8') as f:
    d = json.load(f)
print("\n=== orders in store.json ===")
for o in d.get('orders', []):
    print(f"  num={o.get('order_number')} email={o.get('email')} pwd={o.get('password')} pid={o.get('product_id')} qty={o.get('qty')} status={o.get('status')}")

print("\n=== products ===")
for p in d.get('products', []):
    print(f"  id={p.get('id')} name={p.get('name')} stock={p.get('stock')}")
