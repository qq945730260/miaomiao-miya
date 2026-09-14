import sys
sys.stdout.reconfigure(encoding='utf-8')
path = r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5\server.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

post_start = None
put_start = None
for i, line in enumerate(lines):
    if 'def do_POST' in line:
        post_start = i
    if 'def do_PUT' in line:
        put_start = i
    if post_start and put_start:
        break

print(f"do_POST: lines {post_start+1} to {put_start}")
for i in range(360, 385):
    print(f'{i+1}: {lines[i].rstrip()}')
