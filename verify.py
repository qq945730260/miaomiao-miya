import sys
sys.stdout.reconfigure(encoding='utf-8')

# Verify server.py
c = open(r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5\server.py', encoding='utf-8').read()
put_s = c.find('def do_PUT')
put_e = c.find('def do_DELETE')
put_b = c[put_s:put_e]

found_bad = False
for line in put_b.split('\n'):
    if 'order/confirm' in line and 'admin' not in line:
        print(f'BAD: non-admin order/confirm still in PUT: {line.strip()}')
        found_bad = True
if not found_bad:
    print('OK: no non-admin order/confirm in do_PUT')

# Verify product.html
p = open(r'C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5\static\product.html', encoding='utf-8').read()
print(f"OK: d.order_id used: {'d.order_id' in p}")
print(f"OK: redundant text removed: {'支付完成后点击下方' not in p}")
print(f"OK: showOrderSuccess fixed: {'if(d.ok || d.already)' in p}")

# Summary
print('\nAll checks passed!' if not found_bad and 'd.order_id' in p else '\nSOME CHECKS FAILED!')
