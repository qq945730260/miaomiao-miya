import sys
sys.stdout.reconfigure(encoding='utf-8')
path = r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5\static\js\main.js'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Remove allOrders global (no longer needed)
c = c.replace('var allOrders=[];\n', '', 1)
print("Removed allOrders global:", 'var allOrders' not in c)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

# Final verification of both files
import subprocess, os
env = os.environ.copy()
env['HTTP_PROXY'] = 'http://127.0.0.1:10808'
env['HTTPS_PROXY'] = 'http://127.0.0.1:10808'
repo = r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5'

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=repo, env=env)
    return r.returncode, r.stdout, r.stderr

run(['git', '-c', 'safe.directory=*', 'add', '.'])
r1 = run(['git', '-c', 'safe.directory=*', 'commit', '-q', '-m', 'fix: order query remove status filter + add public /api/sold endpoint'])
print("commit:", r1[0])
r2 = run(['git', '-c', 'safe.directory=*', '-c', 'http.proxy=http://127.0.0.1:10808', '-c', 'https.proxy=http://127.0.0.1:10808', 'push', 'origin', 'v5'])
print("push:", r2[0])
if r2[1]: print("OUT:", r2[1].strip())
if r2[2]: print("ERR:", r2[2].strip()[:200])
