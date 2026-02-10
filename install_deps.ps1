#!/usr/bin/env powershell

# 安装依赖脚本
Write-Host "================================" -ForegroundColor Green
Write-Host "开始安装项目依赖..." -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

# 检查是否存在虚拟环境
if (-not (Test-Path "venv")) {
    Write-Host "创建虚拟环境..." -ForegroundColor Yellow
    python -m venv venv
}

# 激活虚拟环境
Write-Host "激活虚拟环境..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# 升级pip
Write-Host "升级pip..." -ForegroundColor Yellow
pip install --upgrade pip

# 安装依赖
Write-Host "安装项目依赖..." -ForegroundColor Yellow
pip install -r requirements.txt

# 检查安装结果
if ($LASTEXITCODE -eq 0) {
    Write-Host "================================" -ForegroundColor Green
    Write-Host "依赖安装成功！" -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
    Write-Host "下一步：" -ForegroundColor Cyan
    Write-Host "1. 修改 config.py 文件中的配置" -ForegroundColor Cyan
    Write-Host "2. 运行 python run.py 初始化数据库" -ForegroundColor Cyan
    Write-Host "3. 访问 /admin/register 创建管理员账号" -ForegroundColor Cyan
} else {
    Write-Host "================================" -ForegroundColor Red
    Write-Host "依赖安装失败，请检查错误信息" -ForegroundColor Red
    Write-Host "================================" -ForegroundColor Red
    exit 1
}