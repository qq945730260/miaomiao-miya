import os, sys
sys.stdout.reconfigure(encoding='utf-8')
repo = r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5'

# 1. Restore auto_commit() calls in server.py
path = os.path.join(repo, 'server.py')
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Check if auto_commit() calls are missing
ac_count = content.count('auto_commit()')
print(f"Current auto_commit() calls: {ac_count}")

# Add auto_commit() after init_db
if '    auto_commit()\n\n' not in content and 'def init_db' in content:
    # Find end of init_db function
    idx = content.find('    conn.close()\n')
    if idx >= 0:
        # Find the line after conn.close() in init_db
        after = content[idx+len('    conn.close()\n'):]
        if 'auto_commit()' not in after[:200]:
            content = content[:idx+len('    conn.close()\n')] + '    auto_commit()\n' + after
            print("Added auto_commit() after init_db")

# Add auto_commit() after product POST (around line ~275 area)
# Look for pattern: conn.close()\n            send_json(self, dict(row)
content2 = content.replace(
    '            conn.close()\n            send_json(self, dict(row) if row else {}, 201)',
    '            conn.close()\n            auto_commit()\n            send_json(self, dict(row) if row else {}, 201)'
)
if content2 != content:
    content = content2
    print("Added auto_commit() after product POST")

# Add auto_commit() after upload
content3 = content.replace(
    '                    return send_json(self, {"filename": sn})',
    '                    auto_commit()\n                    return send_json(self, {"filename": sn})'
)
if content3 != content:
    content = content3
    print("Added auto_commit() after upload")

# Add auto_commit() after order create
content4 = content.replace(
    '            conn.close()\n            send_json(self, {"ok": True, "order_id": oid',
    '            conn.close()\n            auto_commit()\n            send_json(self, {"ok": True, "order_id": oid'
)
if content4 != content:
    content = content4
    print("Added auto_commit() after order create")

# Add auto_commit() after settings PUT
content5 = content.replace(
    '            conn.commit()\n            conn.close()\n            send_json(self, {"ok": True})\n        elif path == "/api/categories"',
    '            conn.commit()\n            conn.close()\n            auto_commit()\n            send_json(self, {"ok": True})\n        elif path == "/api/categories"'
)
if content5 != content:
    content = content5
    print("Added auto_commit() after settings PUT")

# Add auto_commit() after order confirm
content6 = content.replace(
    '            conn.commit()\n            conn.close()\n            send_json(self, {"ok": True})\n        elif path == "/api/admin/order/confirm"',
    '            conn.commit()\n            conn.close()\n            auto_commit()\n            send_json(self, {"ok": True})\n        elif path == "/api/admin/order/confirm"'
)
if content6 != content:
    content = content6
    print("Added auto_commit() after order confirm")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"Final auto_commit() count: {content.count('auto_commit()')}")

# 2. Remove sync button from admin.html
admin_path = os.path.join(repo, 'static', 'admin.html')
with open(admin_path, 'r', encoding='utf-8') as f:
    admin_content = f.read()

# Remove the sync button line
admin_content = admin_content.replace(
    "    <button class=\"btn btn-sm\" onclick=\"doSync()\" id=\"sync-btn\" style=\"margin-left:12px;background:#7BC89A;color:#fff;\" title=\"手动同步数据到云端\">↻ 同步数据</button>\n",
    ''
)
# Also remove doSync function
import re
admin_content = re.sub(r'\nfunction doSync\(\)\{[^}]+\}[\s\S]*?\n\}', '\n', admin_content)
admin_content = re.sub(r'\nfunction doSync\(\)\{[\s\S]*?catch\(function\(\)\{[^}]+\}\);[\s\n]*\}', '', admin_content)

with open(admin_path, 'w', encoding='utf-8') as f:
    f.write(admin_content)
print("Sync button and doSync function removed from admin.html")
print("Done!")
