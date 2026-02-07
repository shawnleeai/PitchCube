# PitchCube 部署指南

本文档详细介绍如何部署 PitchCube 应用到各种环境。

## 目录

1. [快速部署（Docker Compose）](#快速部署docker-compose)
2. [生产环境部署](#生产环境部署)
3. [环境变量配置](#环境变量配置)
4. [API 密钥配置](#api-密钥配置)
5. [故障排查](#故障排查)

---

## 快速部署（Docker Compose）

这是最简单的部署方式，适合快速体验或开发测试。

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 4GB+ 可用内存

### 部署步骤

```bash
# 1. 克隆项目（或使用已下载的代码）
cd pitchcube-new

# 2. 创建环境变量文件
cp .env.example .env

# 3. 编辑 .env 文件，配置必要参数
# 至少需要修改：
# - MONGODB_PASSWORD（数据库密码）
# - JWT_SECRET_KEY（JWT密钥）

# 4. 启动服务
docker-compose up -d

# 5. 查看服务状态
docker-compose ps

# 6. 访问应用
# 前端界面: http://localhost:3000
# API 文档: http://localhost:8000/docs
# 健康检查: http://localhost:8000/health
```

### 停止服务

```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷（谨慎使用）
docker-compose down -v
```

---

## 生产环境部署

### 架构建议

```
                    ┌─────────────┐
                    │   Nginx     │  ← SSL/TLS, 负载均衡
                    │   (443)     │
                    └──────┬──────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
    ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
    │  Frontend   │ │  Frontend   │ │  Frontend   │
    │  Instance 1 │ │  Instance 2 │ │  Instance N │
    └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
           │               │               │
           └───────────────┼───────────────┘
                           │
                    ┌──────▼──────┐
                    │  Backend    │  ← 多个实例
                    │   API       │
                    └──────┬──────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
    ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
    │  MongoDB    │ │   Redis     │ │ Cloud       │
    │  ReplicaSet │ │   Cluster   │ │  Storage    │
    └─────────────┘ └─────────────┘ └─────────────┘
```

### 使用 Docker Swarm 部署

```bash
# 1. 初始化 Swarm
docker swarm init

# 2. 部署应用
docker stack deploy -c docker-compose.yml pitchcube

# 3. 查看服务状态
docker service ls

# 4. 扩容后端服务
docker service scale pitchcube_backend=3
```

### 使用 Kubernetes 部署

```bash
# 1. 创建命名空间
kubectl create namespace pitchcube

# 2. 应用配置
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/mongodb.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml
kubectl apply -f k8s/ingress.yaml

# 3. 查看状态
kubectl get pods -n pitchcube
```

---

## 环境变量配置

### 必需配置

| 变量名 | 描述 | 示例值 |
|--------|------|--------|
| `JWT_SECRET_KEY` | JWT签名密钥（生产环境必须修改） | `your-random-secret-key` |
| `MONGODB_PASSWORD` | MongoDB管理员密码 | `secure-password-123` |

### 可选配置（AI功能）

| 变量名 | 描述 | 获取方式 |
|--------|------|----------|
| `OPENAI_API_KEY` | OpenAI API密钥 | [platform.openai.com](https://platform.openai.com) |
| `STABILITY_API_KEY` | Stability AI密钥 | [platform.stability.ai](https://platform.stability.ai) |
| `AZURE_SPEECH_KEY` | Azure语音服务密钥 | [Azure Portal](https://portal.azure.com) |
| `AZURE_SPEECH_REGION` | Azure服务区域 | `eastasia` |

### 安全配置最佳实践

1. **生成强密钥**
   ```bash
   # JWT Secret (32+ characters)
   openssl rand -base64 32
   
   # MongoDB Password
   openssl rand -base64 24
   ```

2. **使用环境变量文件**
   ```bash
   # 确保 .env 文件权限正确
   chmod 600 .env
   ```

3. **生产环境使用密钥管理服务**
   - AWS Secrets Manager
   - Azure Key Vault
   - HashiCorp Vault
   - Kubernetes Secrets

---

## API 密钥配置

### 获取 API 密钥

#### OpenAI API

1. 访问 [platform.openai.com](https://platform.openai.com)
2. 注册/登录账号
3. 进入 "API keys" 页面
4. 点击 "Create new secret key"
5. **重要**：立即复制密钥（只显示一次）

#### Stability AI

1. 访问 [platform.stability.ai](https://platform.stability.ai)
2. 创建账号
3. 进入 "API Keys" 页面
4. 生成新密钥

#### Azure Speech Services

1. 访问 [Azure Portal](https://portal.azure.com)
2. 创建 "Speech Services" 资源
3. 在 "Keys and Endpoint" 中获取密钥和区域

### 安全使用 API 密钥

1. **密钥存储**
   ```bash
   # 正确：使用环境变量
   OPENAI_API_KEY=sk-xxx
   
   # 错误：不要硬编码在代码中
   # api_key = "sk-xxx"  # ❌ 永远不要这样做
   ```

2. **密钥轮换**
   - 定期更换 API 密钥
   - 为不同环境使用不同密钥
   - 启用 API 密钥使用监控

3. **使用限制**
   - 设置配额限制防止意外超支
   - 监控 API 调用频率
   - 启用异常使用告警

---

## 故障排查

### 常见问题

#### 1. 服务无法启动

```bash
# 检查日志
docker-compose logs

# 检查具体服务
docker-compose logs backend
docker-compose logs frontend

# 检查端口占用
netstat -tlnp | grep -E "(3000|8000|27017|6379)"
```

#### 2. 数据库连接失败

```bash
# 检查 MongoDB 状态
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"

# 检查网络连接
docker-compose exec backend ping mongodb

# 重置数据库（会丢失数据）
docker-compose down -v
docker-compose up -d
```

#### 3. API 调用返回 401/403

- 检查 JWT_SECRET_KEY 是否配置正确
- 检查请求头中的 Authorization Token
- 检查 Token 是否过期

#### 4. 前端无法连接后端

- 检查 NEXT_PUBLIC_API_URL 环境变量
- 检查 CORS 配置
- 检查网络连通性

### 性能优化

1. **启用 Gzip 压缩**
2. **配置 CDN**（生产环境）
3. **数据库索引优化**
4. **启用 Redis 缓存**

### 日志监控

```bash
# 实时查看日志
docker-compose logs -f

# 导出日志
docker-compose logs > pitchcube-$(date +%Y%m%d).log
```

---

## 升级指南

```bash
# 1. 备份数据
docker-compose exec mongodb mongodump --out /data/backup

# 2. 拉取最新代码
git pull origin main

# 3. 重新构建镜像
docker-compose build --no-cache

# 4. 重启服务
docker-compose up -d

# 5. 验证升级
curl http://localhost:8000/health
```

---

## 支持与反馈

遇到问题？请通过以下方式获取帮助：

- GitHub Issues: [提交问题](https://github.com/yourusername/pitchcube/issues)
- 文档: [完整文档](../usage/USER_GUIDE.md)
- API 参考: [API 文档](../api/API.md)
