import sys
sys.stdout.reconfigure(encoding='utf-8')
path = r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5\static\js\main.js'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Show loadSettings and the area around buildCard
idx1 = c.find('function loadSettings')
idx2 = c.find('function buildCard')
print(c[idx1:idx2+300])
