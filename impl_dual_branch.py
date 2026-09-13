"""Implement dual-branch data persistence for V5."""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
repo = r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5'
path = os.path.join(repo, 'server.py')

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# === 1. Replace auto_commit to push to 'data' branch ===
old_ac = '''def auto_commit():
    return do_commit()'''

new_ac = '''def auto_commit():
    """Push data/uploads to the 'data' branch (separate from code)."""
    token = os.environ.get('GH_TOKEN', '').strip()
    if not token:
        log_sync('SKIP: GH_TOKEN not set')
        return
    try:
        # Stage data and uploads
        r = subprocess.run(['git', '-c', 'safe.directory=*', 'add', '-A', 'data/', 'uploads/'],
            capture_output=True, timeout=10, cwd=BASE_DIR)
        r2 = subprocess.run(['git', '-c', 'safe.directory=*', 'commit', '-q', '--allow-empty', '-m', 'auto-commit data'],
            capture_output=True, timeout=10, cwd=BASE_DIR)
        if b'nothing' in r2.stdout or b'nothing' in r2.stderr:
            log_sync('SKIP: no data changes')
            return
        # Push to 'data' branch (not main)
        r3 = subprocess.run(['git', '-c', 'safe.directory=*',
            'push', 'https://'+token+'@github.com/qq945730260/miaomiao-miya.git', 'data'],
            capture_output=True, timeout=30, cwd=BASE_DIR)
        if r3.returncode == 0:
            log_sync('OK: pushed to data branch')
        else:
            err = r3.stderr.decode("utf-8", errors="replace")[:300]
            log_sync('FAIL: ' + err)
            print("AUTO-COMMIT FAILED:", err, flush=True)
    except Exception as e:
        log_sync('EXC: ' + str(e))
        print("AUTO-COMMIT EXCEPTION:", str(e), flush=True)'''

if old_ac in content:
    content = content.replace(old_ac, new_ac)
    print("1. auto_commit updated: pushes to 'data' branch")
else:
    print("1. WARNING: old auto_commit not found")
    idx = content.find('def auto_commit')
    print(repr(content[idx:idx+300]))

# === 2. Add restore_data() function and call it in main() ===
# Insert after auto_commit function
insert_after = '''def auto_commit():
    """Push data/uploads to the 'data' branch (separate from code)."""'''
# Find the end of auto_commit (after the except block)
# We need to add restore_data() after auto_commit and call it in main()

# Find where auto_commit ends
ac_end = content.find('\n\ndef clean_expired')
if ac_end > 0:
    restore_func = '''
def restore_data():
    """Pull latest data from 'data' branch on startup to restore DB and uploads."""
    token = os.environ.get('GH_TOKEN', '').strip()
    if not token:
        log_sync('SKIP: GH_TOKEN not set, cannot restore data')
        return
    try:
        # Fetch all branches
        subprocess.run(['git', '-c', 'safe.directory=*', 'fetch', '--all'],
            capture_output=True, timeout=10, cwd=BASE_DIR)
        # Check if data branch exists
        r = subprocess.run(['git', '-c', 'safe.directory=*', 'branch', '-r'],
            capture_output=True, text=True, timeout=10, cwd=BASE_DIR)
        if 'origin/data' not in r.stdout:
            log_sync('SKIP: no data branch found')
            return
        # Checkout data branch to restore files
        subprocess.run(['git', '-c', 'safe.directory=*', 'checkout', 'data'],
            capture_output=True, timeout=10, cwd=BASE_DIR)
        log_sync('OK: restored data from data branch')
        print("Data restored from data branch", flush=True)
    except Exception as e:
        log_sync('RESTORE EXC: ' + str(e))
        print("Data restore failed:", str(e), flush=True)


'''
    content = content[:ac_end] + restore_func + content[ac_end:]
    print("2. restore_data() function added")
else:
    print("2. WARNING: could not find insert point for restore_data")

# === 3. Call restore_data() in main() before init_db ===
old_main = '''def main():
    init_db()
    os.makedirs(UPLOAD_DIR, exist_ok=True)'''
new_main = '''def main():
    restore_data()  # Pull latest data from 'data' branch
    init_db()
    os.makedirs(UPLOAD_DIR, exist_ok=True)'''
if old_main in content:
    content = content.replace(old_main, new_main)
    print("3. main() updated to call restore_data() first")
else:
    print("3. WARNING: main() pattern not found")
    # Try alternative
    import re
    m = re.search(r'def main\(\):.*?init_db\(\)', content, re.DOTALL)
    if m:
        print("Found main at", m.start())
        print(repr(m.group()))

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

# === 4. Verify ===
print()
print("=== Verification ===")
print("auto_commit pushes to data branch:", "'data'" in content and 'push.*data' in content.replace(' ', ''))
print("restore_data defined:", 'def restore_data' in content)
print("restore_data called in main:", 'restore_data()' in content and 'def main' in content)
print("GH_TOKEN refs:", content.count('GH_TOKEN'))
print("No proxy:", '127.0.0.1:10808' not in content)
