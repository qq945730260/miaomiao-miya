import subprocess, sys, os
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

scripts = ['add_debug.py','check_live.py','check_query.py','check_query2.py','debug_both.py',
           'debug_both2.py','fix_server.py','fix_client.py','fix_sold*.py','debug_q*.py',
           'gp.py','gp2.py','cleanup.py','verify.py']
for s in scripts:
    import glob
    for f in glob.glob(s):
        run(['git', '-c', 'safe.directory=*', 'rm', '-f', f])
        print(f'removed {f}')

run(['git', '-c', 'safe.directory=*', 'commit', '-q', '-m', 'cleanup debug scripts'])
r = run(['git', '-c', 'safe.directory=*', '-c', 'http.proxy=http://127.0.0.1:10808', '-c', 'https.proxy=http://127.0.0.1:10808', 'push', 'origin', 'v5'])
print('final push exit:', r)
