path = r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v6\server.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the broken rstrip lines - replace the broken pattern with correct one
content = content.replace(
    'data=file_bytes.rstrip(b"\n"),\n',
    'data=file_bytes.rstrip(b"\\r\\n"),\n'
)
content = content.replace(
    'f.write(file_bytes.rstrip(b"\n"))\n',
    'f.write(file_bytes.rstrip(b"\\r\\n"))\n'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed rstrip lines')
