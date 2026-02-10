<div align="center">

# 🛍️ 云初の小店 - Yunchu's Shop

**一款现代化的电商网站系统，基于Flask构建**

<p align="center">
  <a href="#简介"><strong>简介</strong></a> •
  <a href="#功能特性"><strong>功能特性</strong></a> •
  <a href="#技术栈"><strong>技术栈</strong></a> •
  <a href="#安装"><strong>安装</strong></a> •
  <a href="#截图"><strong>截图</strong></a>
</p>

![License](https://img.shields.io/github/license/Yunchu-Team/Yunchu-Shop?color=blue&style=flat-square)
![Python](https://img.shields.io/badge/Python-3.8+-3776ab?logo=python&logoColor=white&style=flat-square)
![Flask](https://img.shields.io/badge/Flask-2.3+-000000?logo=flask&logoColor=white&style=flat-square)
![SQLite](https://img.shields.io/badge/SQLite-3+-003b4d?logo=sqlite&logoColor=white&style=flat-square)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952b3?logo=bootstrap&logoColor=white&style=flat-square)
![Last Commit](https://img.shields.io/github/last-commit/Yunchu-Team/Yunchu-Shop?style=flat-square)

</div>

## 💡 简介

**云初の小店** 是一款现代化的电商网站系统，采用Flask框架构建，支持商品管理、订单处理、用户管理等功能。该项目旨在为小型电商提供一套完整的解决方案。

- 🛠️ **功能齐全** - 包含商品、订单、用户、优惠码等完整电商功能
- 👥 **邀请返利** - 支持用户邀请返利系统，促进用户增长
- 💰 **提现系统** - 用户可申请提现，管理员后台审核处理
- 🎨 **响应式设计** - 适配各种设备，提供良好用户体验
- 🔐 **安全可靠** - 采用多种安全措施保护用户数据

## 🌟 功能特性

### 📦 核心功能
- **商品管理** - 添加、编辑、删除商品，支持分类和标签
- **订单管理** - 完整的订单处理流程，支持多种状态
- **用户管理** - 用户注册、登录、个人中心管理
- **购物车系统** - 支持添加、修改、删除购物车商品

### 💎 高级功能
- **邀请返利** - 邀请好友获得佣金，支持多级返利
- **优惠码系统** - 支持满减、折扣等多种优惠形式
- **卡密管理** - 自动发货卡密商品
- **提现系统** - 用户收益提现，管理员审核处理
- **站点配置** - 后台可配置站点信息、支付方式等

### 🎯 特色功能
- **响应式设计** - 完美适配桌面端和移动端
- **多支付方式** - 支持微信、支付宝、银行卡支付
- **订单状态追踪** - 实时查看订单状态变化
- **数据统计** - 后台数据统计和分析

## 🛠️ 技术栈

| 类别 | 技术/工具 |
|------|----------|
| **后端框架** | Flask 2.3+ |
| **数据库** | SQLite 3+, SQLAlchemy 2.0+ |
| **用户认证** | Flask-Login, Flask-Bcrypt |
| **表单验证** | Flask-WTF |
| **前端框架** | Bootstrap 5, jQuery |
| **图标库** | Bootstrap Icons |
| **缓存** | Flask-Caching |
| **图片处理** | Pillow |
| **部署** | WSGI (Gunicorn/Nginx) |

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Git
- 支持JavaScript的现代浏览器

### 安装步骤

#### 1. 克隆项目
```bash
git clone https://github.com/Yunchu-Team/shop-opensource.git
cd shop-opensource
```

#### 2. 创建虚拟环境
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### 3. 安装依赖
```bash
pip install -r requirements.txt
```

#### 4. 配置项目
```bash
# 编辑配置文件
nano config.py
```

修改以下配置：
- `SECRET_KEY` - 设置为安全的随机字符串
- `DATABASE_URL` - 如需使用其他数据库，修改此项
- `UPLOAD_FOLDER` - 确保上传目录存在且可写

#### 5. 初始化数据库
```bash
python run.py
```

#### 6. 启动项目
```bash
python run.py
```

访问 `http://localhost:5091` 即可使用

## 📸 截图预览

<div align="center">
<img width="1347" height="817" alt="image" src="https://github.com/user-attachments/assets/9c154c33-e00e-4d39-8f9e-1d350041ef38" />
<img width="1452" height="745" alt="image" src="https://github.com/user-attachments/assets/e7bdf831-07ff-4374-9f43-ae92ef5b7598" />
<img width="1337" height="745" alt="image" src="https://github.com/user-attachments/assets/1c265e52-4532-4872-81a3-f3103c19e303" />
<img width="1351" height="580" alt="image" src="https://github.com/user-attachments/assets/63008778-c4ef-4928-bd8a-11485a9ae219" />
</div>

## 📋 配置说明

### 环境变量配置
项目支持通过环境变量进行配置：

```bash
# .env 文件示例
SECRET_KEY=your-very-secure-secret-key-here
DATABASE_URL=sqlite:///site.db
UPLOAD_FOLDER=app/static/uploads
ORDER_STATE_DATA_DIR=data/order_states
NEZHA_URL=https://nezha.example.com
NEZHA_TOKEN=your-nezha-monitor-token
```

### 生产环境部署
```bash
# 使用Gunicorn部署
gunicorn -w 4 -b 0.0.0.0:8000 run:app

# 配合Nginx反向代理
```

## 🤝 贡献

我们欢迎任何形式的贡献！

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 Apache 2.0 许可证 - 查看 [LICENSE](LICENSE) 文件了解更多详情

## 📞 支持

如需技术支持，请联系：[hiyo-qly@foxmail.com](mailto:hiyo-qly@foxmail.com)

## 🏗️ 开发团队

<div align="center">

**YunchuTeam**

[![GitHub](https://img.shields.io/badge/GitHub-Yunchu--Team-181717?logo=github&logoColor=white&style=for-the-badge)](https://github.com/Yunchu-Team)

</div>

---

<div align="center">

⭐ 如果这个项目对你有帮助，请给我们一个 Star！

</div>
