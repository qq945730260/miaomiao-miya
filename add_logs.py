import re
path = 'server.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace('def api_get(table, columns=\
*\, filters=None, order=None, limit=None):', 'def api_get(table, columns=\*\, filters=None, order=None, limit=None):\n    print(f\api_get:
table
\, flush=True)')
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
