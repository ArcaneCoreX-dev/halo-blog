@echo off
chcp 65001 >nul
title Halo Blog 停止

echo.
echo  正在停止 Halo Blog...
docker compose down
echo.
echo  [√] Halo Blog 已停止
echo.
echo  数据已保留，下次启动运行「一键启动.bat」即可。
echo.
pause
