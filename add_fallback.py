with open(r"C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5\server.py","r",encoding="utf-8") as f:
    lines = f.readlines()

# Find main() function and add fallback after load_store()
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    new_lines.append(line)
    # After "store = load_store()", add fallback check
    if 'store = load_store()' in line and i > 580:  # In main() function
        # Add fallback logic
        new_lines.append('    # If no data loaded, use embedded defaults\n')
        new_lines.append('    if not store.get("products") and not store.get("categories"):\n')
        new_lines.append('        print("WARNING: No data, using embedded defaults", flush=True)\n')
        new_lines.append('        store = {\n')
        new_lines.append('            "products": [\n')
        new_lines.append('                {"id": 1, "name": "金渐层A", "title": "金渐层幼猫A窝", "category": "金渐层猫", "price": 2300.0, "stock": 5, "image": "placeholder.jpg", "detail_image": "", "description": "精品金渐层", "wechat": "", "qq": ""},\n')
        new_lines.append('                {"id": 2, "name": "银渐层B", "title": "银渐层幼猫B窝", "category": "银渐层猫", "price": 2100.0, "stock": 3, "image": "placeholder.jpg", "detail_image": "", "description": "银渐层小猫", "wechat": "", "qq": ""},\n')
        new_lines.append('                {"id": 3, "name": "宠物指甲剪", "title": "Miozaa宠物指甲剪猫狗通用保护血线", "category": "宠物用品", "price": 9.0, "stock": 18, "image": "placeholder.jpg", "detail_image": "", "description": "宠物指甲剪", "wechat": "", "qq": ""}\n')
        new_lines.append('            ],\n')
        new_lines.append('            "categories": [\n')
        new_lines.append('                {"id": 1, "name": "全部", "sort_order": 0},\n')
        new_lines.append('                {"id": 2, "name": "宠物用品", "sort_order": 1},\n')
        new_lines.append('                {"id": 3, "name": "金渐层猫", "sort_order": 2},\n')
        new_lines.append('                {"id": 4, "name": "银渐层猫", "sort_order": 3}\n')
        new_lines.append('            ],\n')
        new_lines.append('            "orders": [],\n')
        new_lines.append('            "settings": {"site_title": "喵喵咪丫", "shop_description": "让每一只小猫咪找到温暖的家", "wechat_pay_qr": "", "alipay_qr": "", "wechat_qr": "", "shop_logo": ""},\n')
        new_lines.append('            "admin": {"username": ADMIN_USER, "password": ADMIN_PASS}\n')
        new_lines.append('        }\n')
    i += 1

with open(r"C:\Users\Admin\Documents\ChatGPT\个人网站-260909\miaomiao-miya-v5\server.py","w",encoding="utf-8") as f:
    f.writelines(new_lines)
print("Added fallback data to main()")
