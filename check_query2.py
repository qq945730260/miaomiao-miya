import sys, json, re
sys.stdout.reconfigure(encoding='utf-8')

# Check main.js doQueryOrder fully
with open(r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5\static\js\main.js', encoding='utf-8') as f:
    js = f.read()

idx = js.find('doQueryOrder()')
print("=== doQueryOrder ===")
print(js[idx:idx+700])

print()
# Check index.html modal structure  
with open(r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5\static\index.html', encoding='utf-8') as f:
    html = f.read()
idx2 = html.find('order-query-modal')
print("=== index.html query modal ===")
print(html[idx2:idx2+500])

print()
# Check server order/create response
with open(r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5\server.py', encoding='utf-8') as f:
    sc = f.read()
idx3 = sc.find('/api/order/create')
print("=== order/create response ===")
end_idx = sc.find('elif path', idx3)
print(sc[idx3:end_idx])
