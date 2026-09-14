import sys, json, re
sys.stdout.reconfigure(encoding='utf-8')

# Check server.py order/query handler
with open(r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5\server.py', encoding='utf-8') as f:
    sc = f.read()

idx = sc.find('/api/order/query')
print("=== order/query handler ===")
print(sc[idx:idx+500])

print()
# Check store.json
with open(r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5\data\store.json', encoding='utf-8') as f:
    d = json.load(f)
print("=== orders ===")
for o in d.get('orders', []):
    print(f"  num={o.get('order_number')} email={o.get('email')} pwd={o.get('password')} pid={o.get('product_id')} qty={o.get('qty')} status={o.get('status')}")
print()
print("=== products ===")
for p in d.get('products', []):
    print(f"  id={p.get('id')} name={p.get('name')} stock={p.get('stock')}")

print()
# Check if status filter is removed
print("has pending filter:", 'status") == "pending"' in sc)
print("has /api/sold:", '/api/sold' in sc)
