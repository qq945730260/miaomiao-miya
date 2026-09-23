# 喵喵咪丫 V7 — 项目框架与功能参考标准

> 最后更新：2026-09-23 | 分支：v7 | 部署：Render

---

## 一、项目概述

纯静态/服务端渲染宠物店展示网站，无数据库服务，JSON 本地存储 + Render 持久卷，Python http.server 独立服务。

**访问地址：**
- Render：https://miaomiao-miya.onrender.com
- Cloudflare 域名：https://miaomiao.au0817.dpdns.org（已屏蔽 /admin 访问）

**仓库：** https://github.com/qq945730260/miaomiao-miya

---

## 二、技术栈

| 层 | 技术 |
|----|------|
| 后端 | Python 3，内置 http.server（BaseHTTPRequestHandler） |
| 数据库 | JSON 文件存储（data/store.json），Render 持久卷挂载 |
| 前端 | 原生 HTML + CSS + Vanilla JS，无框架 |
| 部署 | Render（Python buildpack），静态文件从 /static 服务 |
| CDN/域名 | Cloudflare 代理，绑定 miaomiao.au0817.dpdns.org |

---

## 三、项目结构

```
miaomiao-miya-v7/
├── server.py           # 主服务（路由/API/认证/数据存储）
├── render.yaml         # Render 部署配置（含持久卷）
├── .gitignore
├── static/
│   ├── index.html      # 首页
│   ├── product.html    # 商品详情页
│   ├── admin.html      # 后台管理页
│   ├── css/style.css   # 全局样式
│   └── js/
│       ├── main.js     # 首页 JS（分类导航/商品列表/订单查询）
│       └── admin.js    # 后台 JS
├── data/               # JSON 数据存储目录（持久卷挂载点）
│   ├── store.json      # 主数据文件
│   ├── sync.log        # 同步日志
│   └── .gitkeep
└── uploads/            # 图片上传目录（持久卷挂载点）
    └── .gitkeep
```

---

## 四、数据存储格式

### store.json 结构

```json
{
  "products": [...],
  "categories": [...],
  "orders": [...],
  "settings": {
    "site_title": "喵喵咪丫",
    "shop_description": "",
    "shop_logo": "",
    "wechat_qr": "",
    "wechat_pay_qr": "",
    "alipay_qr": ""
  },
  "admin": {"username": "xuxu", "password": "5361172"}
}
```

---

## 五、API 端点

### 公开接口
- GET /api/settings - 站点设置
- GET /api/categories - 分类列表
- GET /api/products - 商品列表
- POST /api/order/create - 创建订单
- POST /api/order/query - 查询订单
- POST /api/order/confirm - 确认支付

### 需认证接口
- POST /api/admin/login - 登录
- POST /api/admin/change_password - 修改密码
- POST /api/categories - 新增分类
- DELETE /api/categories?id=X - 删除分类
- POST /api/products - 新增商品
- PUT /api/products?id=X - 编辑商品
- DELETE /api/products?id=X - 删除商品
- POST /api/upload - 上传图片
- POST /api/settings - 保存设置
- POST /api/admin/sync - 手动同步到 GitHub

---

## 六、核心功能

1. **后台安全**：/admin 入口，Cloudflare 屏蔽，24h Session
2. **分类管理**：增删改排序，首页导航栏
3. **商品管理**：标题≤60字，库存显示，销量累计
4. **订单查询**：邮箱+6-8位数字密码，7天后自动清除
5. **支付收款**：微信/支付宝静态二维码，确认支付后扣库存

---

## 七、关键配置

```python
ADMIN_USER = "xuxu"
ADMIN_PASS = "5361172"
SESSION_TTL = 86400
MAX_PRODUCTS = 30
BLOCKED_DOMAIN = "miaomiao.au0817.dpdns.org"
ORDER_RETENTION_DAYS = 7
```

---

## 八、Render 部署

### 环境变量
- `GH_TOKEN` = ghp_xxx...（GitHub Token）
- `PYTHON_VERSION` = 3.11.0
- `RENDER_EXTERNAL_VOLUME` = /home/miaomiao/data

### 持久化原理
1. 启动时检测 RENDER_EXTERNAL_VOLUME
2. 使用持久卷路径读写数据
3. 每次保存自动推送到 GitHub
4. 后台提供"同步到 GitHub"按钮

---

## 九、修复历史

| 版本 | 问题 | 修复 |
|------|------|------|
| V4.1 | 分类添加报网络错误 | 去掉 require_auth |
| V5 | 数据休眠后丢失 | 改用 JSON 存储 |
| V6 | Git push 静默失败 | 修复 token 拼写 |
| V7 | git 远端未配置 | 添加 ensure_git_remote() |

---

## 十、部署步骤

1. 推送代码：`git push origin v7`
2. Render Dashboard → Redeploy（选最新 commit）
3. 验证：访问 `/api/debug` 查看 sync_log