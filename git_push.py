import subprocess, sys, os
sys.stdout.reconfigure(encoding='utf-8')
repo = r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5'
env = os.environ.copy()
env['HTTP_PROXY'] = 'http://127.0.0.1:10808'
env['HTTPS_PROXY'] = 'http://127.0.0.1:10808'

def run(cmd, **kwargs):
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=repo, env=env, **kwargs)
    if r.stdout: print('OUT:', r.stdout.strip())
    if r.stderr: print('ERR:', r.stderr.strip())
    return r.returncode

run(['git', '-c', 'safe.directory=*', 'add', '.'])
run(['git', '-c', 'safe.directory=*', 'commit', '-q', '-m', 'fix order confirm to POST'])
r = run(['git', '-c', 'safe.directory=*', '-c', 'http.proxy=http://127.0.0.1:10808', '-c', 'https.proxy=http://127.0.0.1:10808', 'push', 'origin', 'v5'])
print('exit:', r.returncode)
