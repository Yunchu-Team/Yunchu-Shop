<div align="center">

# 🛍️ Yunchu's Shop - 云初の小店

**A modern e-commerce website system built with Flask**

<p align="center">
  <a href="#introduction"><strong>Introduction</strong></a> •
  <a href="#features"><strong>Features</strong></a> •
  <a href="#tech-stack"><strong>Tech Stack</strong></a> •
  <a href="#installation"><strong>Installation</strong></a> •
  <a href="#screenshots"><strong>Screenshots</strong></a>
</p>

![License](https://img.shields.io/github/license/Yunchu-Team/Yunchu-Shop?color=blue&style=flat-square)
![Python](https://img.shields.io/badge/Python-3.8+-3776ab?logo=python&logoColor=white&style=flat-square)
![Flask](https://img.shields.io/badge/Flask-2.3+-000000?logo=flask&logoColor=white&style=flat-square)
![SQLite](https://img.shields.io/badge/SQLite-3+-003b4d?logo=sqlite&logoColor=white&style=flat-square)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952b3?logo=bootstrap&logoColor=white&style=flat-square)
![Last Commit](https://img.shields.io/github/last-commit/Yunchu-Team/Yunchu-Shop?style=flat-square)

</div>

## 💡 Introduction

**Yunchu's Shop** is a modern e-commerce website system built with Flask framework, supporting product management, order processing, user management, and more. This project aims to provide a complete solution for small e-commerce platforms.

- 🛠️ **Full Featured** - Complete e-commerce features including products, orders, users, discount codes
- 👥 **Affiliate Program** - User invitation referral system to promote user growth
- 💰 **Withdrawal System** - Users can apply for withdrawals, reviewed by admin backend
- 🎨 **Responsive Design** - Compatible with various devices, providing excellent user experience
- 🔐 **Secure & Reliable** - Multiple security measures to protect user data

## 🌟 Features

### 📦 Core Features
- **Product Management** - Add, edit, delete products with categories and tags
- **Order Management** - Complete order processing workflow with multiple statuses
- **User Management** - User registration, login, personal center management
- **Shopping Cart** - Add, modify, delete shopping cart items

### 💎 Advanced Features
- **Affiliate Referral** - Invite friends to earn commissions, multi-level referral support
- **Discount System** - Supports various discount forms like amount reduction, percentage discounts
- **CD-Key Management** - Automatic delivery of CD-Key products
- **Withdrawal System** - User earnings withdrawal, admin review and processing
- **Site Configuration** - Configure site information, payment methods in backend

### 🎯 Special Features
- **Responsive Design** - Perfect compatibility with desktop and mobile devices
- **Multiple Payment Methods** - Supports WeChat, Alipay, Bank Card payments
- **Order Tracking** - Real-time order status tracking
- **Data Statistics** - Backend data statistics and analysis

## 🛠️ Tech Stack

| Category | Technology/Tool |
|----------|-----------------|
| **Backend Framework** | Flask 2.3+ |
| **Database** | SQLite 3+, SQLAlchemy 2.0+ |
| **Authentication** | Flask-Login, Flask-Bcrypt |
| **Form Validation** | Flask-WTF |
| **Frontend Framework** | Bootstrap 5, jQuery |
| **Icon Library** | Bootstrap Icons |
| **Caching** | Flask-Caching |
| **Image Processing** | Pillow |
| **Deployment** | WSGI (Gunicorn/Nginx) |

## 🚀 Quick Start

### Requirements
- Python 3.8+
- Git
- Modern browser with JavaScript support

### Installation Steps

#### 1. Clone the Project
```bash
git clone https://github.com/Yunchu-Team/shop-opensource.git
cd shop-opensource
```

#### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Configure Project
```bash
# Edit configuration file
nano config.py
```

Modify the following configurations:
- `SECRET_KEY` - Set to a secure random string
- `DATABASE_URL` - Modify if using other databases
- `UPLOAD_FOLDER` - Ensure upload directory exists and is writable

#### 5. Initialize Database
```bash
python run.py
```

#### 6. Start the Project
```bash
python run.py
```

Visit `http://localhost:5091` to use the application

## 📸 Screenshots Preview

<div align="center">

![Homepage](https://via.placeholder.com/800x450/3498db/ffffff?text=Homepage+View)
![Product List](https://via.placeholder.com/800x450/e74c3c/ffffff?text=Product+List+View)
![Admin Dashboard](https://via.placeholder.com/800x450/2ecc71/ffffff?text=Admin+Dashboard+View)

</div>

## 📋 Configuration Guide

### Environment Variables
The project supports configuration via environment variables:

```bash
# .env file example
SECRET_KEY=your-very-secure-secret-key-here
DATABASE_URL=sqlite:///site.db
UPLOAD_FOLDER=app/static/uploads
ORDER_STATE_DATA_DIR=data/order_states
NEZHA_URL=https://nezha.example.com
NEZHA_TOKEN=your-nezha-monitor-token
```

### Production Deployment
```bash
# Deploy with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 run:app

# With Nginx reverse proxy
```

## 🤝 Contributing

We welcome contributions of any kind!

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## 📞 Support

For technical support, please contact: [hiyo-qly@foxmail.com](mailto:hiyo-qly@foxmail.com)

## 🏗️ Development Team

<div align="center">

**YunchuTeam**

[![GitHub](https://img.shields.io/badge/GitHub-Yunchu--Team-181717?logo=github&logoColor=white&style=for-the-badge)](https://github.com/Yunchu-Team)

</div>

---

<div align="center">

⭐ If this project is helpful to you, please give us a Star!

</div>