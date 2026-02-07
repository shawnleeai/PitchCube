#!/usr/bin/env python3
"""
PitchCube 启动脚本
同时启动后端和前端服务
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def check_port(port):
    """检查端口是否被占用"""
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    except:
        return False

def main():
    print_header("PitchCube 启动器")
    
    # 获取项目根目录
    root_dir = Path(__file__).parent.absolute()
    backend_dir = root_dir / "backend"
    frontend_dir = root_dir / "frontend"
    
    print(f"项目目录: {root_dir}")
    print(f"后端目录: {backend_dir}")
    print(f"前端目录: {frontend_dir}")
    print()
    
    # 检查端口
    if check_port(8000):
        print("[警告] 端口 8000 已被占用，请先关闭占用该端口的程序")
        return 1
    
    if check_port(3000):
        print("[警告] 端口 3000 已被占用，请先关闭占用该端口的程序")
        return 1
    
    # 创建必要目录
    (backend_dir / "generated").mkdir(exist_ok=True)
    (backend_dir / "static").mkdir(exist_ok=True)
    
    processes = []
    
    try:
        # 启动后端
        print("[1/3] 启动后端服务...")
        print("      URL: http://localhost:8000")
        print("      API文档: http://localhost:8000/docs")
        print()
        
        backend_cmd = [
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ]
        
        backend_process = subprocess.Popen(
            backend_cmd,
            cwd=backend_dir,
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
        )
        processes.append(("后端", backend_process))
        
        # 等待后端启动
        print("      等待后端启动...")
        time.sleep(3)
        
        # 检查后端是否成功启动
        try:
            import urllib.request
            urllib.request.urlopen("http://localhost:8000/health", timeout=5)
            print("      [OK] 后端服务已启动")
        except Exception as e:
            print(f"      [警告] 后端可能未完全启动: {e}")
        
        print()
        
        # 启动前端
        print("[2/3] 启动前端服务...")
        print("      URL: http://localhost:3000")
        print()
        
        # 先检查npm_modules是否存在
        if not (frontend_dir / "node_modules").exists():
            print("      首次运行，安装前端依赖...")
            subprocess.run(["npm", "install"], cwd=frontend_dir, shell=True)
        
        frontend_cmd = ["npm", "run", "dev"]
        
        frontend_process = subprocess.Popen(
            frontend_cmd,
            cwd=frontend_dir,
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
        )
        processes.append(("前端", frontend_process))
        
        # 等待前端启动
        print("      等待前端启动...")
        time.sleep(5)
        
        print("      [OK] 前端服务已启动")
        print()
        
        # 打开浏览器
        print("[3/3] 打开浏览器...")
        webbrowser.open("http://localhost:3000")
        
        print_header("服务启动完成！")
        print("访问地址:")
        print("  前端界面: http://localhost:3000")
        print("  后端API:  http://localhost:8000")
        print("  API文档:  http://localhost:8000/docs")
        print()
        print("按 Ctrl+C 停止所有服务")
        print()
        
        # 等待用户中断
        try:
            while True:
                time.sleep(1)
                # 检查进程是否还在运行
                for name, proc in processes:
                    if proc.poll() is not None:
                        print(f"[警告] {name} 服务已退出")
                        return 1
        except KeyboardInterrupt:
            print("\n\n正在停止服务...")
            
    finally:
        # 停止所有进程
        for name, proc in processes:
            print(f"停止 {name} 服务...")
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except:
                proc.kill()
        
        print_header("服务已停止")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
