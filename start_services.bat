@echo off
chcp 65001 >nul
echo ==========================================
echo   PitchCube 服务启动器
echo ==========================================
echo.

:: 获取脚本所在目录
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo 📂 工作目录: %CD%
echo.

:: 启动后端
echo 🚀 正在启动后端 API 服务器...
echo    地址: http://localhost:8000
echo    文档: http://localhost:8000/docs
echo.

start "PitchCube Backend" cmd /k "cd /d "%SCRIPT_DIR%\backend" && echo 正在启动后端... && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 && pause"

echo ⏳ 等待后端启动 (5秒)...
timeout /t 5 /nobreak >nul

:: 启动前端
echo.
echo 🎨 正在启动前端开发服务器...
echo    地址: http://localhost:3000
echo.

start "PitchCube Frontend" cmd /k "cd /d "%SCRIPT_DIR%\frontend" && echo 正在启动前端... && npm run dev && pause"

echo ⏳ 等待前端启动 (5秒)...
timeout /t 5 /nobreak >nul

echo.
echo ==========================================
echo  ✅ 服务启动完成！
echo ==========================================
echo.
echo 📱 访问地址:
echo    前端界面: http://localhost:3000
echo    后端API:  http://localhost:8000
echo    API文档:  http://localhost:8000/docs
echo    健康检查: http://localhost:8000/health
echo.
echo 🛑 停止服务:
echo    关闭标题为 'PitchCube Backend' 的窗口
echo    关闭标题为 'PitchCube Frontend' 的窗口
echo.
echo 💡 提示:
echo    - 请检查是否弹出了两个命令行窗口
echo    - 后端窗口应显示 'Uvicorn running on http://0.0.0.0:8000'
echo    - 前端窗口应显示 'Ready on http://localhost:3000'
echo    - 如果窗口闪退，请检查Python和Node.js是否安装正确
echo.

:: 尝试自动打开浏览器
echo 🌐 正在尝试打开浏览器...
timeout /t 2 /nobreak >nul
start http://localhost:3000

echo.
echo 如果浏览器没有自动打开，请手动访问: http://localhost:3000
echo.
pause
