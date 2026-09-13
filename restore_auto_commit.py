"""Restore auto_commit for V5 - automatic sync after each data write."""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
repo = r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5'
path = os.path.join(repo, 'server.py')
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace do_commit + auto_commit with auto-commit that logs failures
old_funcs = '''SYNC_LOG = os.path.join(BASE_DIR, "data", "sync.log")

def log_sync(msg):
    try:
        os.makedirs(os.path.dirname(SYNC_LOG), exist_ok=True)
        with open(SYNC_LOG, "a", encoding="utf-8") as f:
            f.write(time.strftime("%Y-%m-%d %H:%M:%S") + " " + msg + "\\n")
    except Exception:
        pass

def do_commit(force=False):
    """Commit and push data/uploads to git."""
    token = os.environ.get('GH_TOKEN', '').strip()
    if not token:
        log_sync('SKIP: GH_TOKEN not set')
        return {"ok": False, "error": "GH_TOKEN未配置"}
    try:
        r = subprocess.run(['git', '-c', 'safe.directory=*', 'add', '-A', 'data/', 'uploads/'],
            capture_output=True, timeout=10, cwd=BASE_DIR)
        r2 = subprocess.run(['git', '-c', 'safe.directory=*', 'commit', '-q', '--allow-empty', '-m', 'auto-commit data'],
            capture_output=True, timeout=10, cwd=BASE_DIR)
        changed = b'nothing' not in r2.stdout and b'nothing' not in r2.stderr
        if not changed and not force:
            log_sync('SKIP: no changes')
            return {"ok": True, "message": "no_changes"}
        if changed or force:
            r3 = subprocess.run(['git', '-c', 'safe.directory=*',
                'push', 'https://'+token+'@github.com/qq945730260/miaomiao-miya.git', 'main'],
                capture_output=True, timeout=30, cwd=BASE_DIR)
            if r3.returncode == 0:
                log_sync('OK: pushed')
                return {"ok": True, "message": "已同步到云端"}
            else:
                err = r3.stderr.decode("utf-8", errors="replace")[:300]
                log_sync('FAIL: ' + err)
                return {"ok": False, "error": err}
    except Exception as e:
        log_sync('EXC: ' + str(e))
        return {"ok": False, "error": str(e)}


def auto_commit():
    return do_commit()'''

new_funcs = '''SYNC_LOG = os.path.join(BASE_DIR, "data", "sync.log")

def log_sync(msg):
    try:
        os.makedirs(os.path.dirname(SYNC_LOG), exist_ok=True)
        with open(SYNC_LOG, "a", encoding="utf-8") as f:
            f.write(time.strftime("%Y-%m-%d %H:%M:%S") + " " + msg + "\\n")
    except Exception:
        pass

def auto_commit():
    """Commit and push data/uploads to git after each write."""
    token = os.environ.get('GH_TOKEN', '').strip()
    if not token:
        log_sync('SKIP: GH_TOKEN not set in env')
        return
    try:
        r = subprocess.run(['git', '-c', 'safe.directory=*', 'add', '-A', 'data/', 'uploads/'],
            capture_output=True, timeout=10, cwd=BASE_DIR)
        r2 = subprocess.run(['git', '-c', 'safe.directory=*', 'commit', '-q', '--allow-empty', '-m', 'auto-commit data'],
            capture_output=True, timeout=10, cwd=BASE_DIR)
        if b'nothing' in r2.stdout or b'nothing' in r2.stderr:
            log_sync('SKIP: no changes to commit')
            return
        r3 = subprocess.run(['git', '-c', 'safe.directory=*',
            'push', 'https://'+token+'@github.com/qq945730260/miaomiao-miya.git', 'main'],
            capture_output=True, timeout=30, cwd=BASE_DIR)
        if r3.returncode == 0:
            log_sync('OK: push successful')
        else:
            err = r3.stderr.decode("utf-8", errors="replace")[:300]
            log_sync('FAIL: ' + err)
            print("AUTO-COMMIT FAILED:", err, flush=True)
    except Exception as e:
        log_sync('EXC: ' + str(e))
        print("AUTO-COMMIT EXCEPTION:", str(e), flush=True)'''

if old_funcs in content:
    content = content.replace(old_funcs, new_funcs)
    print("1. auto_commit restored with logging")
else:
    print("1. WARNING: old func block not found")
    idx = content.find('def do_commit')
    if idx >= 0:
        print("Found do_commit at", idx)
    else:
        print("do_commit not found")

# 2. Remove /api/admin/sync endpoint (no longer needed)
if '/api/admin/sync' in content:
    # Find and remove the sync handler
    import re
    content = re.sub(r'\s*elif path == \"/api/admin/sync\":\s*\n\s*if not require_auth\(self\):\s*\n\s*return send_json\(self, \{"error": "unauthorized"\}, 401\)\s*\n\s*result = do_commit\(force=True\)\s*\n\s*send_json\(self, result\)\s*\n', '\n', content)
    print("2. Removed /api/admin/sync endpoint")

# 3. Remove sync button from admin.html
admin_path = os.path.join(repo, 'static', 'admin.html')
with open(admin_path, 'r', encoding='utf-8') as f:
    admin_content = f.read()
# Remove sync button
admin_content = admin_content.replace(
    '    <button class="btn btn-sm" onclick="doSync()" id="sync-btn" style="margin-left:12px;background:#7BC89A;color:#fff;" title="手动同步数据到云端">↻ 同步数据</button>',
    ''
)
# Remove doSync function
admin_content = admin_content.replace('''
function doSync(){
  var btn=document.getElementById('sync-btn');
  if(!btn)return;
  btn.disabled=true;btn.textContent='同步中...';
  fetch('/api/admin/sync',{method:'POST',headers:{"Content-Type":"application/json"}})
    .then(function(r){return r.json();})
    .then(function(d){
      btn.disabled=false;
      if(d.ok){btn.textContent='✓ 已同步';setTimeout(function(){btn.textContent='↻ 同步数据';},2000);toast(d.message||'同步成功');}
      else{btn.textContent='↻ 同步数据';toast(d.error||'同步失败');}
    })
    .catch(function(){btn.disabled=false;btn.textContent='↻ 同步数据';toast('网络错误');});
}''', '')
with open(admin_path, 'w', encoding='utf-8') as f:
    f.write(admin_content)
print("3. Removed sync button from admin.html")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print()
print("=== Verification ===")
print("auto_commit calls:", content.count('auto_commit()'))
print("log_sync defined:", 'def log_sync' in content)
print("/api/admin/sync removed:", '/api/admin/sync' not in content)
print("sync button removed:", 'sync-btn' not in admin_content)
