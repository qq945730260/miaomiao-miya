import subprocess, sys, os
sys.stdout.reconfigure(encoding='utf-8')
repo = r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5'
env = os.environ.copy()
env['HTTP_PROXY'] = 'http://127.0.0.1:10808'
env['HTTPS_PROXY'] = 'http://127.0.0.1:10808'

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=repo, env=env)
    if r.stdout: print('OUT:', r.stdout.strip())
    if r.stderr: print('ERR:', r.stderr.strip())
    return r.returncode

# Remove debug scripts from git tracking
scripts = ['debug_q3.py','debug_q4.py','debug_q5.py','debug_query.py',
           'debug_query2.py','debug_sold.py','debug_sold2.py','debug_sold3.py','debug_sold4.py',
           'fix_sold.py','fix_sold2.py','fix_sold3.py','fix_sold4.py','fix_sold_final.py',
           'check2.py','check3.py','check_lines.py','check_server.py','fix_confirm.py',
           'fix_confirm2.py','fix_confirm3.py','fix_confirm4.py','fix_confirm5.py','gp.py']
for s in scripts:
    run(['git', '-c', 'safe.directory=*', 'rm', '-f', s])

run(['git', '-c', 'safe.directory=*', 'commit', '-q', '-m', 'cleanup: remove debug scripts'])
run(['git', '-c', 'safe.directory=*', '-c', 'http.proxy=http://127.0.0.1:10808', '-c', 'https.proxy=http://127.0.0.1:10808', 'push', 'origin', 'v5'])
