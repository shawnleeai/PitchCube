@echo off
echo ============================================
echo    PitchCube 前端服务启动器
echo ============================================
echo.

cd /d "%~dp0\frontend"

echo 正在启动前端服务...
echo 访问: http://localhost:3000
echo.
echo 按 Ctrl+C 停止服务
echo.

npm run dev

pause
