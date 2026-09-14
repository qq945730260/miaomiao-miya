import sys
sys.stdout.reconfigure(encoding='utf-8')
path = r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5\server.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()
idx = c.find('/api/order/query')
print(c[idx:idx+600])
