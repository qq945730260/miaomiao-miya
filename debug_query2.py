import sys
sys.stdout.reconfigure(encoding='utf-8')

# Check full doQueryOrder function in main.js
with open(r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5\static\js\main.js', encoding='utf-8') as f:
    js = f.read()

idx = js.find('doQueryOrder')
print(js[idx:idx+800])
print()

# Check API variable
idx2 = js.find('var API')
if idx2 < 0:
    idx2 = js.find("API =")
print("API line:", js[max(0,idx2-20):idx2+100])
print()

# Check index.html query modal structure
with open(r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5\static\index.html', encoding='utf-8') as f:
    html = f.read()
idx3 = html.find('order-query-modal')
print("=== index.html modal ===")
print(html[idx3:idx3+600])
