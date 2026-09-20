path = r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v6\server.py'
with open(path, 'rb') as f:
    data = f.read()

# Fix: the string b"\r\n" got expanded to actual CR LF bytes inside the source code
# We need to replace b"<CR><LF>" with b"\\r\\n" (the literal characters)
# The broken pattern is: b"\r\n" where \r\n are actual bytes 0x0D 0x0A
data = data.replace(b'rstrip(b"\r\n")', b'rstrip(b"\\r\\n")')
data = data.replace(b'rstrip(b"\r\n\r\n")', b'rstrip(b"\\r\\n")')

with open(path, 'wb') as f:
    f.write(data)
print('Fixed raw bytes')
