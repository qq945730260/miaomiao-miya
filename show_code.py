import sys
sys.stdout.reconfigure(encoding='utf-8')
path = r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5\server.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

idx1 = c.find('def main():')
idx2 = c.find('\n\ndef ', idx1)
print("=== main() ===")
print(c[idx1:idx2])

idx3 = c.find('def auto_commit()')
idx4 = c.find('\n\ndef ', idx3)
print("\n=== auto_commit() ===")
print(c[idx3:idx4])
