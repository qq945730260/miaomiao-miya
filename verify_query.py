import sys
sys.stdout.reconfigure(encoding='utf-8')
path = r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5\static\js\main.js'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

idx = c.find('doQueryOrder()')
print(c[idx:idx+800])
print()
print("checks:")
print("  d.order_number:", 'd.order_number' in c)
print("  d.id in query func:", 'd.id' in c[idx:idx+800])
print("  订单编号:", '订单编号' in c)
