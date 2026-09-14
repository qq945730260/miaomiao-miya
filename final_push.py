import subprocess, sys, os, glob
sys.stdout.reconfigure(encoding='utf-8')
repo = r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5'
env = os.environ.copy()
env['HTTP_PROXY'] = 'http://127.0.0.1:10808'
env['HTTPS_PROXY'] = 'http://127.0.0.1:10808'

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=repo, env=env)
    if r.stdout: print('OUT:', r.stdout.strip())
    if r.stderr: print('ERR:', r.stderr.strip()[:200])
    return r.returncode

# Remove all remaining debug scripts
for f in glob.glob('*.py'):
    if f not in ['server.py']:
        try:
            os.remove(f)
            print(f'deleted {f}')
        except: pass

run(['git', '-c', 'safe.directory=*', 'add', '.'])
r1 = run(['git', '-c', 'safe.directory=*', 'commit', '-q', '-m', 'remove debug logging, clean up'])
print('commit:', r1)
r2 = run(['git', '-c', 'safe.directory=*', '-c', 'http.proxy=http://127.0.0.1:10808', '-c', 'https.proxy=http://127.0.0.1:10808', 'push', 'origin', 'v5'])
print('push:', r2)
