import sys, json
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open(r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5\data\store.json', encoding='utf-8'))
print('orders:', len(d.get('orders', [])))
for o in d.get('orders', []):
    print(f"  num={o.get('order_number')} pid={o.get('product_id')} qty={o.get('qty')} status={o.get('status')}")
print('products:', len(d.get('products', [])))
for p in d.get('products', []):
    print(f"  id={p.get('id')} name={p.get('name')} stock={p.get('stock')}")
