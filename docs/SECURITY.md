# PitchCube 安全指南

本文档详细介绍 PitchCube 的安全特性以及如何安全地使用 API 密钥。

## 目录

1. [API 密钥安全](#api-密钥安全)
2. [数据隐私](#数据隐私)
3. [安全最佳实践](#安全最佳实践)
4. [安全事件响应](#安全事件响应)

---

## API 密钥安全

### 什么是 API 密钥？

API 密钥是访问外部 AI 服务（如 OpenAI、Stability AI）的凭证。PitchCube 使用这些服务来增强生成功能，但**所有 API 密钥都是可选的**。

### API 密钥存储安全

#### ✅ 正确做法

```bash
# 1. 使用环境变量文件
cp .env.example .env
# 编辑 .env 文件，填入密钥

# 2. 确保 .env 不被提交到 Git
echo ".env" >> .gitignore
git add .gitignore

# 3. 设置正确的文件权限（Linux/Mac）
chmod 600 .env
```

#### ❌ 错误做法

```python
# 永远不要这样做！
OPENAI_API_KEY = "sk-abc123..."  # ❌ 硬编码密钥

# 不要提交到 Git
git add .env  # ❌ 不要这样做！
```

### 生产环境密钥管理

#### 选项 1：Docker Secrets（推荐）

```yaml
# docker-compose.yml
services:
  backend:
    secrets:
      - openai_api_key
      - jwt_secret

secrets:
  openai_api_key:
    file: ./secrets/openai_api_key.txt
  jwt_secret:
    file: ./secrets/jwt_secret.txt
```

#### 选项 2：云密钥管理服务

**AWS Secrets Manager:**
```python
import boto3
from botocore.exceptions import ClientError

def get_secret():
    secret_name = "pitchcube/production"
    region_name = "us-east-1"
    
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    
    try:
        secret_value = client.get_secret_value(SecretId=secret_name)
        return secret_value['SecretString']
    except ClientError as e:
        raise e
```

**Azure Key Vault:**
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
client = SecretClient(
    vault_url="https://pitchcube.vault.azure.net/",
    credential=credential
)

api_key = client.get_secret("openai-api-key").value
```

#### 选项 3：Kubernetes Secrets

```bash
# 创建 Secret
kubectl create secret generic pitchcube-secrets \
  --from-literal=openai-api-key=sk-xxx \
  --from-literal=jwt-secret=xxx

# 在 Pod 中使用
env:
  - name: OPENAI_API_KEY
    valueFrom:
      secretKeyRef:
        name: pitchcube-secrets
        key: openai-api-key
```

### API 密钥轮换

建议每 90 天轮换一次 API 密钥：

```bash
# 1. 在服务商控制台生成新密钥
# 2. 更新环境变量
# 3. 重启服务
# 4. 验证新密钥工作
# 5. 在服务商控制台删除旧密钥
```

---

## 数据隐私

### 数据收集

PitchCube 收集以下数据：

| 数据类型 | 用途 | 存储位置 |
|----------|------|----------|
| 产品信息 | 生成展示物料 | 本地数据库 |
| 用户账户 | 身份验证 | 本地数据库 |
| 生成记录 | 历史查询 | 本地数据库 |
| 使用统计 | 服务优化 | 本地数据库 |

### 数据安全措施

1. **传输加密**
   - 所有 API 通信使用 HTTPS/TLS 1.3
   - 防止中间人攻击

2. **存储加密**
   - 数据库连接使用 SSL
   - 敏感字段加密存储

3. **访问控制**
   - JWT 身份验证
   - 基于角色的权限控制

### 第三方服务数据

当使用 AI 服务时，数据处理方式：

| 服务商 | 数据处理 | 隐私政策 |
|--------|----------|----------|
| OpenAI | 不用于模型训练 | [链接](https://openai.com/privacy) |
| Stability AI | 不保留生成记录 | [链接](https://stability.ai/privacy) |
| Azure | 企业级隐私保护 | [链接](https://azure.microsoft.com/privacy) |

### 数据删除

用户可以随时删除数据：

```bash
# 删除所有生成记录
curl -X DELETE http://localhost:8000/api/v1/users/me/generations \
  -H "Authorization: Bearer YOUR_TOKEN"

# 删除账户（包括所有数据）
curl -X DELETE http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 安全最佳实践

### 部署安全

1. **使用最新版本**
   ```bash
   # 定期更新依赖
   pip install --upgrade -r requirements.txt
   npm update
   ```

2. **配置防火墙**
   ```bash
   # 仅开放必要端口
   ufw allow 80/tcp
   ufw allow 443/tcp
   ufw deny 27017/tcp  # MongoDB 不对外暴露
   ```

3. **使用 HTTPS**
   ```yaml
   # docker-compose.yml 配合 Nginx
   services:
     nginx:
       image: nginx:alpine
       ports:
         - "80:80"
         - "443:443"
       volumes:
         - ./nginx.conf:/etc/nginx/nginx.conf
         - ./ssl:/etc/nginx/ssl
   ```

### 应用安全

1. **强密码策略**
   - 最小长度 8 位
   - 包含大小写字母、数字、特殊字符
   - 定期更换密码

2. **会话管理**
   - Token 过期时间合理设置
   - 支持会话注销
   - 检测异常登录

3. **输入验证**
   - 所有用户输入经过验证
   - 防止 SQL 注入
   - 防止 XSS 攻击

### 监控与审计

1. **日志记录**
   ```python
   # 记录关键操作
   logger.info(f"User {user_id} generated poster for product {product_id}")
   ```

2. **异常监控**
   - 配置错误告警
   - 监控 API 调用频率
   - 检测异常行为

---

## 安全事件响应

### 发现密钥泄露

如果怀疑 API 密钥泄露：

1. **立即撤销密钥**
   - 登录对应服务商控制台
   - 立即删除/撤销泄露的密钥

2. **更换密钥**
   - 生成新的 API 密钥
   - 更新应用配置
   - 重启服务

3. **检查日志**
   - 查看 API 调用记录
   - 确认是否有异常使用
   - 评估影响范围

4. **通知相关方**
   - 通知团队成员
   - 必要时通知用户

### 报告安全漏洞

如果你发现了安全漏洞，请：

1. **不要公开披露**
2. **发送邮件至**：security@pitchcube.app
3. **包含信息**：
   - 漏洞描述
   - 复现步骤
   - 可能的影响
   - 建议的修复方案

我们承诺：
- 48 小时内确认收到报告
- 7 个工作日内提供修复计划
- 修复后公开致谢（如果你愿意）

---

## 安全检查清单

部署前请确认：

- [ ] 所有默认密码已修改
- [ ] API 密钥存储在环境变量中
- [ ] .env 文件在 .gitignore 中
- [ ] HTTPS 已启用
- [ ] 数据库不对外暴露
- [ ] 日志不包含敏感信息
- [ ] 依赖项已更新到最新版本
- [ ] 防火墙规则已配置
- [ ] 备份策略已制定

---

**记住：安全是每个人的责任！**
