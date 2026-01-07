# MySQL 数据库配置指南

## ✅ 系统要求

本系统现已配置为 **仅使用 MySQL 数据库**（已删除所有 SQLite 支持）。

### 必须安装:
- MySQL 5.7+ 或 8.0+
- Python 3.9+
- Node.js 16+

---

## 🔧 数据库配置

### MySQL 连接参数

**配置文件**: `backend/.env`

```dotenv
# MySQL 数据库配置
DB_USER=root
DB_PASSWORD=AAAaaa211
DB_HOST=localhost
DB_PORT=3306
DB_NAME=jieke

# 或者使用完整的 DATABASE_URL
DATABASE_URL=mysql+pymysql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}
```

### 当前配置值

| 参数   | 值          |
| ------ | ----------- |
| 主机   | `localhost` |
| 端口   | `3306`      |
| 用户   | `root`      |
| 密码   | `AAAaaa211` |
| 数据库 | `jieke`     |

---

## 🚀 快速启动流程

### 1️⃣ 验证 MySQL 连接

```bash
# 测试 MySQL 连接
mysql -h localhost -u root -pAAAaaa211

# 列出数据库
SHOW DATABASES;

# 选择 jieke 数据库
USE jieke;

# 显示表
SHOW TABLES;

# 退出
EXIT;
```

### 2️⃣ 初始化系统

```bash
# 进入项目目录
cd E:\python_demo\tumorDetection\tumorDetection

# 运行 MySQL 检查和初始化脚本
python check_mysql.py
```

**预期输出:**
```
======================================================================
MySQL 数据库连接验证和初始化
======================================================================

当前配置:
  Host: localhost
  Port: 3306
  User: root
  Database: jieke

----------------------------------------------------------------------
第一步：测试数据库连接...
----------------------------------------------------------------------
✓ 数据库 URI: mysql+pymysql://root:***@localhost:3306/jieke
测试连接...
✓ MySQL 连接成功

----------------------------------------------------------------------
第二步：创建数据库表...
----------------------------------------------------------------------
✓ 数据库表创建成功

----------------------------------------------------------------------
第三步：初始化默认用户...
----------------------------------------------------------------------
✓ admin 用户已存在
  ID: 1
  Email: admin@example.com
  Active: True
  Admin: True

======================================================================
✓ 所有检查通过！
======================================================================
```

### 3️⃣ 启动后端服务

```bash
# 进入项目根目录
cd E:\python_demo\tumorDetection\tumorDetection

# 启动后端
python -m backend.main

# 或者
cd backend && python main.py
```

**预期输出:**
```
 * Running on http://127.0.0.1:8000
```

### 4️⃣ 启动前端服务

```bash
# 打开新的终端窗口

# 进入前端目录
cd E:\python_demo\tumorDetection\tumorDetection\frontend

# 启动开发服务器
npm run dev
```

**预期输出:**
```
  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

### 5️⃣ 访问应用

打开浏览器访问: **http://localhost:5173**

**登录凭证:**
- 用户名: `admin`
- 密码: `admin123`

---

## 🔍 数据库验证命令

### 检查表是否创建

```sql
USE jieke;
SHOW TABLES;
```

**应该看到:**
```
+----------------------+
| Tables_in_jieke      |
+----------------------+
| users                |
| medical_images       |
| ... (其他表)         |
+----------------------+
```

### 检查 admin 用户

```sql
USE jieke;
SELECT * FROM users WHERE username='admin';
```

**应该看到:**
```
+----+----------+---------------------+-----------+---------------------+-----------+----------+
| id | username | email               | password_ | created_at          | is_active | is_admin |
+----+----------+---------------------+-----------+---------------------+-----------+----------+
|  1 | admin    | admin@example.com   | (hash)    | 2026-01-04 ...      |         1 |        1 |
+----+----------+---------------------+-----------+---------------------+-----------+----------+
```

### 检查表结构

```sql
USE jieke;
DESCRIBE users;
DESCRIBE medical_images;
```

---

## ❌ 故障排查

### 问题 1: MySQL 连接拒绝

**错误信息:**
```
pymysql.err.OperationalError: (2003, "Can't connect to MySQL server on 'localhost' (10061)")
```

**解决方案:**
```bash
# 1. 检查 MySQL 是否运行
# Windows:
tasklist | findstr mysql
# 如果没有显示，启动 MySQL 服务

# 2. 检查连接参数
# 确保 host/port/user/password 正确

# 3. 重启 MySQL 服务
# Windows 命令行 (以管理员身份):
net stop MySQL80
net start MySQL80

# 如果是其他版本，替换 MySQL80 为相应版本
```

### 问题 2: 数据库不存在

**错误信息:**
```
pymysql.err.ProgrammingError: (1049, "Unknown database 'jieke'")
```

**解决方案:**
```bash
# 创建数据库
mysql -h localhost -u root -pAAAaaa211

# 在 MySQL 命令行中:
CREATE DATABASE IF NOT EXISTS jieke;
EXIT;

# 然后再运行初始化脚本
python check_mysql.py
```

### 问题 3: 用户权限不足

**错误信息:**
```
pymysql.err.OperationalError: (1045, "Access denied for user 'root'@'localhost'")
```

**解决方案:**
```bash
# 检查密码是否正确
mysql -h localhost -u root -pAAAaaa211

# 如果不对，重置密码或更新 .env 文件
```

### 问题 4: 前端无法连接后端

**症状:** 前端显示 API 错误

**检查:**
```bash
# 1. 确保后端正在运行
netstat -ano | findstr :8000

# 2. 测试后端健康检查
curl http://127.0.0.1:8000/health

# 3. 检查前端中的 API 配置
# 文件: frontend/.env 或 frontend/src/services/api.ts
# 确保 VITE_API_BASE_URL 指向 http://127.0.0.1:8000
```

---

## 📊 系统架构

```
┌──────────────────────────────────────────┐
│   浏览器 (http://localhost:5173)         │
│       前端 (Vue 3 + TypeScript)          │
└─────────────────┬────────────────────────┘
                  │ HTTP/REST API
                  │
┌─────────────────▼────────────────────────┐
│  后端服务 (http://127.0.0.1:8000)       │
│      Flask 3.0.0 + SQLAlchemy            │
│  ├─ /api/auth      (认证)               │
│  ├─ /api/medical   (医学影像)           │
│  ├─ /api/results   (结果显示)           │
│  ├─ /api/admin     (管理员)             │
│  └─ /api/dashboard (仪表盘)             │
└─────────────────┬────────────────────────┘
                  │ SQLAlchemy ORM
                  │ PyMySQL Driver
                  │
┌─────────────────▼────────────────────────┐
│  MySQL 数据库 (localhost:3306)          │
│  Database: jieke                         │
│  User: root                              │
│  ├─ users                                │
│  ├─ medical_images                       │
│  ├─ ... (其他表)                        │
└──────────────────────────────────────────┘
```

---

## ✨ SQLite 迁移说明

系统已完全迁移到 MySQL，所有 SQLite 相关代码已删除：

- ✅ `main.py` 中的 SQLite 默认选项已移除
- ✅ 强制使用 MySQL 连接字符串
- ✅ 所有环境变量默认值已设置为 MySQL
- ✅ 医学图像模型已优化为 MySQL 的 LONGTEXT 类型

### 数据迁移

如果之前有 SQLite 数据，需要手动迁移到 MySQL：

```bash
# 1. 从 SQLite 导出数据
sqlite3 tumor_detection.db .dump > export.sql

# 2. 修改 SQL 以兼容 MySQL
# (可能需要调整数据类型和语法)

# 3. 导入到 MySQL
mysql -h localhost -u root -pAAAaaa211 jieke < export.sql
```

---

## 🔐 安全建议

在生产环境中，请：

1. **更改默认密码**
   ```bash
   # 在 MySQL 中为 root 用户设置强密码
   mysql -h localhost -u root -pAAAaaa211
   ALTER USER 'root'@'localhost' IDENTIFIED BY 'your_strong_password';
   ```

2. **创建专用数据库用户**
   ```sql
   CREATE USER 'tumor_detection'@'localhost' IDENTIFIED BY 'strong_password';
   GRANT ALL PRIVILEGES ON jieke.* TO 'tumor_detection'@'localhost';
   FLUSH PRIVILEGES;
   ```

3. **更新 .env 文件**
   ```dotenv
   DB_USER=tumor_detection
   DB_PASSWORD=strong_password
   ```

4. **设置 JWT 密钥**
   ```dotenv
   JWT_SECRET_KEY=your-secure-random-key
   ```

---

## 📞 获取帮助

如有问题，请检查：

1. MySQL 日志
   ```bash
   # Windows: MySQL 日志通常在 MySQL 安装目录下
   # 或查看事件查看器
   ```

2. 应用日志
   ```bash
   # 查看后端控制台输出
   # 查看浏览器开发者工具 (F12)
   ```

3. 数据库连接
   ```bash
   python check_mysql.py
   ```

---

祝你使用愉快！🎉
