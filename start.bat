#!/bin/bash
# PitchCube 服务启动脚本

echo "=========================================="
echo "  PitchCube 服务启动器"
echo "=========================================="
echo ""

# 启动后端
echo "🚀 正在启动后端 API 服务器..."
echo "   地址: http://localhost:8000"
echo "   文档: http://localhost:8000/docs"
cd backend
start cmd /k "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
cd ..

echo ""
echo "⏳ 等待后端启动 (3秒)..."
sleep 3

# 启动前端
echo ""
echo "🎨 正在启动前端开发服务器..."
echo "   地址: http://localhost:3000"
cd frontend
start cmd /k "npm run dev"
cd ..

echo ""
echo "=========================================="
echo "  ✅ 服务启动完成！"
echo "=========================================="
echo ""
echo "📱 访问地址:"
echo "   前端界面: http://localhost:3000"
echo "   后端API:  http://localhost:8000"
echo "   API文档:  http://localhost:8000/docs"
echo "   健康检查: http://localhost:8000/health"
echo ""
echo "🛑 停止服务:"
echo "   - 关闭后端的命令行窗口"
echo "   - 关闭前端的命令行窗口"
echo ""
echo "📊 服务状态:"
echo "   后端端口: 8000"
echo "   前端端口: 3000"
echo ""
echo "💡 提示:"
echo "   - 首次启动可能需要一些时间"
echo "   - 后端窗口显示 'Application startup complete' 表示成功"
echo "   - 前端窗口显示 'Ready on http://localhost:3000' 表示成功"
echo ""
