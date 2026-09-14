import sys
sys.stdout.reconfigure(encoding='utf-8')
path = r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5\static\js\main.js'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Find where stock is displayed in product cards
idx = c.find('库存 '+p.stock)
print("Found stock display at:", idx)
print(c[max(0,idx-100):idx+200])
