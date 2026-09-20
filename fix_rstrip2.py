path = r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v6\server.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# The \r\n got turned into actual newlines in the string literals. Fix them.
# Line 167-169: data=file_bytes.rstrip(b"\r\n"),
content = content.replace(
    'data=file_bytes.rstrip(b"\n"),',
    'data=file_bytes.rstrip(b"\\r\\n"),'
)
content = content.replace(
    'f.write(file_bytes.rstrip(b"\n")),',
    'f.write(file_bytes.rstrip(b"\\r\\n")),'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed rstrip literal')
