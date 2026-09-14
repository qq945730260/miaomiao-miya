import sys, json
sys.stdout.reconfigure(encoding='utf-8')
path = r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5\static\js\main.js'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Find stock display in product cards
import re
m = re.search(r'库存.*?stock', c)
if m:
    print("stock context:", c[max(0,m.start()-80):m.end()+80])

# Find renderProducts or card building
idx = c.find('card-content')
print("\n=== card-content ===")
print(c[max(0,idx-50):idx+300])

# Also find where product list is built
idx2 = c.find('displayProds')
print("\n=== displayProds ===")
print(c[max(0,idx2-30):idx2+500])
