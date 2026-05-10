@echo off
chcp 65001 >nul
title Halo Blog 一键部署

echo.
echo  ========================================
echo   Halo Blog 一键部署脚本
echo  ========================================
echo.

:: 检查 Docker 是否安装
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [错误] 未检测到 Docker Desktop！
    echo.
    echo  请先安装 Docker Desktop：
    echo  https://www.docker.com/products/docker-desktop/
    echo.
    pause
    exit /b 1
)

:: 检查 Docker 是否运行
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo  [错误] Docker Desktop 未启动！
    echo.
    echo  请先启动 Docker Desktop，等待右下角鲸鱼图标变绿后重试。
    echo.
    pause
    exit /b 1
)

echo  [√] Docker 已就绪
echo.

:: 创建必要目录
if not exist "data" mkdir data
if not exist "uploads" mkdir uploads
echo  [√] 数据目录已创建
echo.

:: 构建并启动
echo  正在构建镜像（首次需要 2-3 分钟下载依赖）...
echo.
docker compose build
if %errorlevel% neq 0 (
    echo.
    echo  [错误] 镜像构建失败！请检查网络连接。
    pause
    exit /b 1
)

echo.
echo  正在启动容器...
docker compose up -d
if %errorlevel% neq 0 (
    echo.
    echo  [错误] 容器启动失败！
    pause
    exit /b 1
)

echo.
echo  ========================================
echo   部署完成！
echo  ========================================
echo.
echo   博客前台: http://localhost:8000
echo   管理后台: http://localhost:8000/admin
echo.
echo   默认账号: admin
echo   默认密码: admin123
echo.
echo   首次使用请登录后台修改密码！
echo  ========================================
echo.

:: 自动打开浏览器
echo  正在打开浏览器...
start http://localhost:8000/admin

pause
