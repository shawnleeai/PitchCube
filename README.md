# 🎲 PitchCube - 路演魔方

<p align="center">
  <img src="https://raw.githubusercontent.com/yourusername/pitchcube/main/docs/assets/logo.png" alt="PitchCube Logo" width="200"/>
</p>

<p align="center">
  <strong>AI驱动的路演展示智能魔方平台</strong>
</p>

<p align="center">
  <a href="#-快速开始">快速开始</a> •
  <a href="#-功能特性">功能特性</a> •
  <a href="#-技术栈">技术栈</a> •
  <a href="#-部署指南">部署指南</a> •
  <a href="#-api文档">API文档</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Next.js-15-black?style=flat-square&logo=next.js" />
  <img src="https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat-square&logo=fastapi" />
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python" />
  <img src="https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=flat-square&logo=typescript" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" />
</p>

---

## 📖 项目简介

**PitchCube（路演魔方）** 是一个专为黑客松团队、初创公司、独立开发者和企业创新团队设计的AI驱动路演展示自动化平台。

### 🎯 核心价值主张

**模块化组合，一键生成专业路演展示**。让创作者专注于产品核心价值，AI负责将创意转化为具有冲击力的展示物料，大幅降低路演准备时间，提升展示效果与成功率。

### 💡 解决的问题

- ⏰ **时间压力**：黑客松最后6小时，无暇设计展示物料
- 🎨 **设计门槛**：技术团队缺乏专业设计技能
- 📢 **展示效果**：好产品因展示不佳而被埋没
- 💰 **成本限制**：无法承担专业设计团队费用

---

## ✨ 功能特性

### 🧩 六大魔方模块

| 模块 | 功能描述 | 状态 |
|------|----------|------|
| **🎨 海报工坊** | AI智能海报设计，多尺寸多风格模板 | ✅ 可用 |
| **🎬 视频演播室** | 自动生成视频脚本与演示视频 | ✅ 可用 |
| **🖨️ IP铸造厂** | 3D打印IP形象生成与在线打印 | 🚧 开发中 |
| **🎤 语音解说员** | 智能语音讲解与交互问答 | 🚧 开发中 |
| **👥 协作空间** | 多人实时协作编辑与版本管理 | 📋 规划中 |
| **📊 数据魔镜** | A/B测试分析与优化建议 | 📋 规划中 |

### 🚀 核心能力

- **🤖 AI智能生成**：基于产品资料自动设计海报、生成视频脚本
- **🎨 品牌定制**：支持Logo、品牌色、字体等自定义
- **📱 多平台适配**：自动生成适合各社交平台的尺寸规格
- **⚡ 极速生成**：海报10秒生成，视频脚本30秒完成
- **🔒 隐私安全**：端到端加密，数据本地存储

---

## 🛠️ 技术栈

### 前端
- **Framework**: [Next.js 15](https://nextjs.org/) (App Router)
- **Language**: [TypeScript](https://www.typescriptlang.org/)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/)
- **UI Components**: [shadcn/ui](https://ui.shadcn.com/)
- **State Management**: [Zustand](https://github.com/pmndrs/zustand)
- **Animation**: [Framer Motion](https://www.framer.com/motion/)

### 后端
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Language**: Python 3.11+
- **Database**: MongoDB + PostgreSQL
- **Cache**: Redis
- **Queue**: Celery + Redis
- **Auth**: JWT + OAuth2

### AI 服务（可选增强）
- **Text Generation**: OpenAI GPT-4 / Claude
- **Image Generation**: Stability AI / DALL-E 3
- **Video Generation**: RunwayML / Pika Labs
- **Speech**: Azure Speech Services

---

## 🚀 快速开始

### 方式一：Docker Compose（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/yourusername/pitchcube.git
cd pitchcube

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的配置

# 3. 启动服务
docker-compose up -d

# 4. 访问应用
# 前端: http://localhost:3000
# 后端API: http://localhost:8000
# API文档: http://localhost:8000/docs
```

### 方式二：本地开发

**前置要求：**
- Node.js 18+
- Python 3.11+
- MongoDB 6.0+
- Redis 7.0+

```bash
# 1. 克隆项目
git clone https://github.com/yourusername/pitchcube.git
cd pitchcube

# 2. 配置环境变量
cp .env.example .env

# 3. 安装前端依赖
cd frontend
npm install
npm run dev

# 4. 安装后端依赖（新终端）
cd ../backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# 5. 访问应用
# 前端: http://localhost:3000
# 后端API: http://localhost:8000
```

---

## 📚 文档

| 文档 | 描述 |
|------|------|
| [部署指南](./docs/deployment/DEPLOYMENT.md) | 详细的部署和配置说明 |
| [API文档](./docs/api/API.md) | RESTful API 完整参考 |
| [使用指南](./docs/usage/USER_GUIDE.md) | 用户操作手册和教程 |
| [安全指南](./docs/SECURITY.md) | API密钥管理和安全最佳实践 |
| [贡献指南](./CONTRIBUTING.md) | 如何参与项目贡献 |

---

## 🔐 API 密钥配置

本项目支持与多个 AI 服务集成以增强功能。所有 API 密钥都是**可选的**，应用在没有 API 密钥的情况下也能正常运行（使用模拟数据和预设模板）。

### 支持的 AI 服务

| 服务 | 用途 | 获取方式 |
|------|------|----------|
| OpenAI | 文案生成、视频脚本 | [platform.openai.com](https://platform.openai.com) |
| Stability AI | 高质量海报图片生成 | [platform.stability.ai](https://platform.stability.ai) |
| Azure Speech | 语音合成功能 | [azure.microsoft.com](https://azure.microsoft.com) |

### 安全使用指南

1. **永远不要将 API 密钥提交到 Git**
   ```bash
   # 确保 .env 在 .gitignore 中
   echo ".env" >> .gitignore
   ```

2. **仅在后端使用 API 密钥**
   - 所有 API 调用都通过后端代理
   - 前端不会直接访问 AI 服务

3. **使用环境变量管理密钥**
   ```bash
   # 开发环境
   cp .env.example .env
   # 编辑 .env 填入密钥
   
   # 生产环境建议使用密钥管理服务
   # - AWS Secrets Manager
   # - Azure Key Vault
   # - HashiCorp Vault
   ```

更多安全最佳实践，请参阅 [安全指南](./docs/SECURITY.md)。

---

## 🏗️ 项目结构

```
pitchcube/
├── frontend/              # Next.js 前端应用
│   ├── app/              # App Router 页面
│   ├── components/       # React 组件
│   ├── lib/              # 工具函数
│   └── public/           # 静态资源
├── backend/              # FastAPI 后端服务
│   ├── app/              # 主应用
│   ├── api/              # API 路由
│   ├── models/           # 数据模型
│   ├── services/         # 业务服务
│   └── core/             # 核心配置
├── docs/                 # 项目文档
├── scripts/              # 部署和工具脚本
└── examples/             # 示例数据
```

---

## 🤝 贡献

欢迎贡献代码、报告问题或提出新功能建议！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

请阅读 [贡献指南](./CONTRIBUTING.md) 了解详细信息。

---

## 📄 许可证

本项目采用 [MIT 许可证](./LICENSE)。

---

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 高性能 Python Web 框架
- [Next.js](https://nextjs.org/) - React 应用框架
- [Tailwind CSS](https://tailwindcss.com/) - 实用优先的 CSS 框架
- [shadcn/ui](https://ui.shadcn.com/) - 精美的 UI 组件

---

<p align="center">
  Made with ❤️ by the PitchCube Team
</p>
