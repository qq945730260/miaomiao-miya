# 喵喵咪丫 V4 — 项目框架与功能参考标准

> 最后更新：2026-09-12 | 分支：main | 部署：Render

---

## 一、项目概述

纯静态/服务端渲染宠物店展示网站，无数据库服务，SQLite 本地存储，Python http.server 独立服务。

**访问地址：**
- Render：https://miaomiao-miya.onrender.com
- Cloudflare 域名：https://miaomiao.au0817.dpdns.org（已屏蔽 /admin 访问）

**仓库：** https://github.com/qq945730260/miaomiao-miya

---

## 二、技术栈

| 层 | 技术 |
|----|------|
| 后端 | Python 3，内置 http.server（BaseHTTPRequestHandler） |
| 数据库 | SQLite（data/products.db） |
| 前端 | 原生 HTML + CSS + Vanilla JS，无框架 |
| 部署 | Render（Python buildpack），静态文件从 /static 服务 |
| CDN/域名 | Cloudflare 代理，绑定 miaomiao.au0817.dpdns.org |

---

## 三、项目结构

```
miaomiao-miya-v4/
├── server.py           # 主服务（路由/API/认证/数据库）
├── render.yaml         # Render 部署配置
├── .gitignore
├── static/
│   ├── index.html      # 首页
│   ├── product.html    # 商品详情页
│   ├── admin.html      # 后台管理页
│   ├── css/style.css   # 全局样式
│   └── js/
│       ├── main.js     # 首页 JS（分类导航/商品列表/订单查询）
│       └── admin.js    # 后台 JS
├── data/               # SQLite 数据库目录（部署后自动创建）
│   └── products.db
└── uploads/            # 图片上传目录
```

---

## 四、数据库表结构

### products（商品）
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,          -- 商品名称（旧字段，兼容）
    title TEXT DEFAULT '',       -- 商品标题（≤60字，用于搜索和展示）
    category TEXT NOT NULL,      -- 分类
    price REAL NOT NULL,         -- 价格
    stock INTEGER NOT NULL DEFAULT 0,  -- 库存
    image TEXT DEFAULT 'placeholder.jpg',  -- 头图文件名
    detail_image TEXT DEFAULT '',         -- 详情图文件名
    description TEXT DEFAULT '',   -- 商品描述
    wechat TEXT DEFAULT '',        -- 客服微信
    qq TEXT DEFAULT ''             -- QQ
);
```

### categories（分类）
```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0
);
```
默认三个分类：萌宠(0)、宠物用品(1)、其它(2)

### orders（订单）
```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    password TEXT NOT NULL,       -- 6-8位数字查询密码
    product_id INTEGER NOT NULL,
    qty INTEGER NOT NULL,
    total REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',  -- pending / completed
    created_at TEXT NOT NULL
);
```
订单保留 7 天后自动清除。

### settings（设置）
```sql
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL DEFAULT ''
);
```
关键 key：`site_title`、`site_tagline`、`wechat_pay_qr`、`alipay_qr`

### admin（管理员）
```sql
CREATE TABLE admin (
    username TEXT PRIMARY KEY,
    password TEXT
);
```
默认凭据：`xuxu` / `5361172`

---

## 五、API 端点

### 公开接口（无需登录）
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/settings` | 获取站点设置 |
| GET | `/api/categories` | 获取分类列表（公开） |
| GET | `/api/products?id=X` | 获取单个商品 |
| GET | `/api/products` | 获取全部商品列表 |
| POST | `/api/order/create` | 创建订单 |
| POST | `/api/order/query` | 查询订单（邮箱+密码） |

### 需认证接口（Session Cookie）
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/admin/check` | 检查登录状态 |
| POST | `/api/admin/login` | 登录 |
| POST | `/api/admin/change_password` | 修改密码 |
| POST | `/api/categories` | 新增分类 |
| PUT | `/api/categories` | 更新分类（批量） |
| DELETE | `/api/categories?id=X` | 删除分类 |
| POST | `/api/products` | 新增商品 |
| PUT | `/api/products?id=X` | 编辑商品 |
| DELETE | `/api/products?id=X` | 删除商品 |
| POST | `/api/upload` | 上传图片 |
| GET/POST | `/api/admin/payment_qrcodes` | 收款码设置 |
| PUT | `/api/admin/order/confirm` | 确认订单（扣库存） |
| DELETE | `/api/admin/order/clean` | 清理过期订单 |
| DELETE | `/api/admin/order/delete` | 删除指定订单 |
| GET | `/api/orders` | 获取全部订单 |

---

## 六、核心功能说明

### 1. 后台安全
- 入口：网址末尾加 `/admin`（不暴露链接）
- Cloudflare 二级域名禁止访问 `/admin`，返回 403
- Session 有效期 24 小时（SESSION_TTL = 86400）
- 密码修改：验证旧密码后更新，放在后台最末尾

### 2. 分类管理
- 默认三个：萌宠、宠物用品、其它
- 后台可增删改，支持排序
- 首页顶部 sticky 分类导航栏，点击筛选商品
- GET `/api/categories` 对所有人开放（首页需要）

### 3. 商品管理
- 商品标题 ≤ 60 字，首页卡片和详情页均显示标题
- 头图（1:1 比例上传，列表用 contain 完整显示）
- 详情图（可选，任意比例，详情页完整显示）
- 库存显示在卡片和详情页
- 最多 30 个商品（MAX_PRODUCTS）

### 4. 订单查询
- 购买流程：选数量 → 确认下单 → 输入邮箱+6-8位数字密码 → 创建订单 → 展示收款码
- 首页右上角"查询订单"入口
- 订单 7 天后自动清除（每次请求时检查）
- 后台确认订单后自动扣减库存（status → completed）

### 5. 支付收款
- 后台上传微信/支付宝收款码图片（静态个人码）
- 详情页展示收款码 + 实付金额文字提示
- 不支持动态金额收款码（需商户 API）

---

## 七、关键配置常量（server.py 顶部）

```python
ADMIN_USER = "xuxu"
ADMIN_PASS = "5361172"
SESSION_TTL = 86400          # 24小时
MAX_PRODUCTS = 30
BLOCKED_DOMAIN = "miaomiao.au0817.dpdns.org"
ORDER_RETENTION_DAYS = 7
```

---

## 八、修复历史与经验

| 版本 | 问题 | 修复 |
|------|------|------|
| V4.1 | 分类添加报网络错误 | GET /api/categories 误加了 require_auth，去掉认证检查 |
| V4.2 | 商品详情页比例选择器多余 | 移除 buildRatioBar/setRatio 函数和 HTML |
| V4.3 | 商品卡片图片被裁剪 | card-img 从 object-fit:cover 改为 contain |
| V4.4 | 详情页布局不合理 | 重构为图文左右分栏 + 描述 + 详情图底部 |
| V4.5 | 付款弹窗无返回按钮 | step1 添加"返回"按钮关闭弹窗 |
| 通用 | 代码块误插入错误 HTTP 方法 | do_GET/do_POST/do_DELETE 中不要混入对方的处理器 |

---

## 九、部署步骤

1. 修改代码后推送到 GitHub：
   ```powershell
   git -c safe.directory="*" add -A
   git -c safe.directory="*" commit -m "描述"
   git -c safe.directory="*" -c http.proxy=http://127.0.0.1:10808 push https://TOKEN@github.com/qq945730260/miaomiao-miya.git main
   ```

2. 去 Render Dashboard → miaomiao-miya → Manual Deploy → Deploy latest commit

---

## 十、注意事项

- **服务器是单进程**：所有数据存在本地 SQLite，不要并发写
- **图片上传**：通过 `/api/upload` POST multipart，保存到 uploads/ 目录
- **订单自动清理**：每次请求 `/api/orders` 或 `/api/order/query` 时触发 clean_expired()
- **库存扣减时机**：后台点击"确认"订单时才扣减，不是下单时
- **静态收款码**：不支持自动填金额，需在二维码旁显示金额文字引导用户
