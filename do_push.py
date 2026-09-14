import subprocess, sys, os
sys.stdout.reconfigure(encoding='utf-8')
repo = r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5'
env = os.environ.copy()
env['HTTP_PROXY'] = 'http://127.0.0.1:10808'
env['HTTPS_PROXY'] = 'http://127.0.0.1:10808'

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=repo, env=env)
    return r.returncode, r.stdout.strip(), r.stderr.strip()

run(['git', '-c', 'safe.directory=*', 'add', '-A'])
r1 = run(['git', '-c', 'safe.directory=*', 'commit', '-q', '-m', 'cleanup all debug scripts'])
print('commit:', r1[0], r1[2][:100])
r2 = run(['git', '-c', 'safe.directory=*', '-c', 'http.proxy=http://127.0.0.1:10808', '-c', 'https.proxy=http://127.0.0.1:10808', 'push', 'origin', 'v5'])
print('push:', r2[0], r2[2][:200])
r3 = run(['git', '-c', 'safe.directory=*', 'status', '--short'])
print('status:', r3[1] if r3[1] else 'clean')
