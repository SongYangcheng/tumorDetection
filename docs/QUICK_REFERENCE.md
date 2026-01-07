# 快速参考卡片

## 🚀 一键启动

```bash
# 终端 1 - 初始化和启动后端
python check_mysql.py          # 初始化数据库
python -m backend.main         # 启动后端

# 终端 2 - 启动前端
cd frontend && npm run dev      # 启动前端
```

访问: http://localhost:5173  
登录: admin / admin123

---

## 📋 关键文件位置

```
frontend/src/
├─ services/
│  ├─ api.ts           (所有 API 调用)
│  └─ auth.ts          (认证服务)
├─ views/
│  ├─ LoginView.vue
│  ├─ DashboardView.vue
│  ├─ UploadView.vue
│  └─ ...
└─ router/
   └─ index.ts         (路由配置)

backend/
├─ main.py             (Flask 应用)
├─ routes/
│  ├─ auth.py          (认证路由)
│  ├─ medical_images.py
│  └─ extra_endpoints.py
├─ models/
│  ├─ user.py
│  └─ medical_image.py
└─ .env                (数据库配置)
```

---

## 🔗 API 地址

| 端点   | URL                      | 认证 |
| ------ | ------------------------ | ---- |
| 登录   | POST /api/login          | ✗    |
| 上传   | POST /api/medical/upload | ✓    |
| 检测   | POST /detect             | ✗    |
| 仪表盘 | GET /api/dashboard/stats | ✓    |

---

## 🗄️ 数据库信息

```
Host: localhost
Port: 3306
User: root
Password: AAAaaa211
Database: jieke
Driver: mysql+pymysql
```

---

## 🔑 登录凭证

```
用户名: admin
密码: admin123
```

---

## 📊 API 端点列表

### 认证 (4)
- POST /api/login
- POST /api/register
- GET /api/profile
- POST /api/change-password

### 医学影像 (3)
- POST /api/medical/upload
- GET /api/medical/{id}
- GET /api/medical/list

### 检测分割 (2)
- POST /detect
- POST /api/results/analyze/{id}

### 术前规划 (2)
- POST /api/preop/simulate
- GET /api/preop/load3d

### 影像组学 (2)
- POST /api/radiomics/extract
- POST /api/radiomics/train

### 工作台 (2)
- POST /api/workbench/preprocess
- POST /api/workbench/augment

### 仪表盘 (7)
- GET /api/dashboard/stats
- GET /api/dashboard/cases-trend
- GET /api/dashboard/accuracy-trend
- GET /api/dashboard/dept-dist
- GET /api/dashboard/doctor-dist
- GET /api/dashboard/recent-cases
- GET /api/dashboard/todos

### 管理 (2)
- GET /api/admin/monitor
- GET /api/admin/model

---

## ✅ 验证清单

使用前检查:

- [ ] MySQL 运行中 (`mysql -h localhost -u root -pAAAaaa211`)
- [ ] 数据库 jieke 存在
- [ ] Python 虚拟环境已激活
- [ ] Node.js 依赖已安装 (`npm install`)
- [ ] 后端数据库初始化 (`python check_mysql.py`)

---

## 🐛 快速故障排查

### 问题: 无法连接 MySQL
```bash
# 检查 MySQL 是否运行
mysql -h localhost -u root -pAAAaaa211 -e "SELECT 1;"

# 重启 MySQL
# Windows: net restart MySQL80
# macOS: brew services restart mysql
```

### 问题: 登录失败
```bash
# 重新初始化数据库
python check_mysql.py

# 检查 admin 用户
mysql -h localhost -u root -pAAAaaa211 jieke
SELECT * FROM users WHERE username='admin';
```

### 问题: 前端无法连接后端
```bash
# 检查后端是否运行
netstat -ano | findstr :8000  # Windows
lsof -i :8000                  # macOS/Linux

# 检查 API 基础 URL
# 文件: frontend/src/services/api.ts
# 应该是: http://127.0.0.1:8000
```

### 问题: npm 依赖错误
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

## 📚 重要文档

| 文档                   | 说明               |
| ---------------------- | ------------------ |
| MYSQL_SETUP.md         | MySQL 完整设置指南 |
| SYSTEM_ARCHITECTURE.md | 系统架构和数据流   |
| FRONTEND_API_CHECK.md  | 前端 API 检查报告  |
| QUICK_START_LOGIN.md   | 快速启动指南       |
| STATUS.md              | 系统状态总结       |

---

## 🎯 常用命令

```bash
# 启动后端
python -m backend.main

# 初始化数据库
python check_mysql.py

# 启动前端
cd frontend && npm run dev

# 前端构建
cd frontend && npm run build

# 类型检查
cd frontend && npm run type-check

# MySQL 命令行
mysql -h localhost -u root -pAAAaaa211 jieke
```

---

## 🔗 URLs

| 应用     | 地址                         | 说明       |
| -------- | ---------------------------- | ---------- |
| 前端     | http://localhost:5173        | Vue 3 应用 |
| 后端     | http://127.0.0.1:8000        | Flask API  |
| 健康检查 | http://127.0.0.1:8000/health | 系统状态   |
| API 文档 | http://127.0.0.1:8000/api    | API 列表   |

---

## 💾 备份和恢复

### 备份数据库
```bash
mysqldump -h localhost -u root -pAAAaaa211 jieke > backup.sql
```

### 恢复数据库
```bash
mysql -h localhost -u root -pAAAaaa211 jieke < backup.sql
```

---

## 🔐 安全提示

- ⚠️ 生产环境需要修改默认密码
- ⚠️ 设置强密码替代 AAAaaa211
- ⚠️ 更新 JWT_SECRET_KEY
- ⚠️ 启用 HTTPS
- ⚠️ 定期备份数据库

---

## 📞 支持

遇到问题:
1. 查看相关文档
2. 运行 `python check_mysql.py`
3. 检查浏览器控制台 (F12)
4. 查看后端日志输出

---

**最后更新**: 2026-01-04  
**状态**: ✅ 可以使用
