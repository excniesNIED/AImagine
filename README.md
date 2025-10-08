# AI Gallery (AImagine)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

一个基于 Python FastAPI 后端和 Astro 前端的现代化、多用户、权限分明的 Web 应用，用于高效管理、检索和版本控制 AI 生成的图片及其元数据。图片文件通过与 Openlist（Alist）集成进行存储和访问。

![AI Gallery Screenshot](docs/images/screenshot.png)

## ✨ 核心功能

### 📸 图片管理
- **智能上传**: 支持拖拽上传，自动提取图片元数据
- **版本控制**: 基于已有图片创建新版本，形成完整的创作树
- **批量操作**: 支持批量编辑、批量删除等操作
- **云端存储**: 通过 Openlist 集成，支持多种云存储服务

### 🔍 搜索与过滤
- **全文搜索**: 支持提示词、模型、标签的模糊搜索
- **高级过滤**: 按分类、模型、多标签组合过滤
- **智能推荐**: 基于用户历史和图片标签的智能推荐

### 🏷️ 元数据管理
- **分类系统**: 预设多个分类，支持自定义扩展
- **标签系统**: 灵活的标签管理，支持自动补全
- **模型管理**: 支持各种 AI 模型的管理
- **参数记录**: 完整记录生成参数，方便复现

### 👥 用户系统
- **角色权限**: 管理员/普通用户权限分离
- **资源隔离**: 用户只能管理自己的作品
- **个人空间**: 每个用户独立的创作空间

### 🎨 界面设计
- **响应式设计**: 完美适配桌面、平板、手机
- **深色模式**: 支持深色/浅色主题切换
- **性能优化**: 图片懒加载、虚拟滚动
- **交互友好**: 流畅的动画和操作反馈

## 🛠 技术栈

### 后端
- **框架**: Python 3.9+ & FastAPI
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **ORM**: SQLAlchemy 2.0
- **认证**: JWT (python-jose) + passlib
- **文件存储**: Alist/Openlist 集成
- **API文档**: 自动生成 OpenAPI/Swagger

### 前端
- **框架**: Astro 4.0+
- **UI组件**: Vue.js 3.4+ 交互组件
- **样式**: Tailwind CSS + PrimeVue
- **状态管理**: Pinia
- **HTTP客户端**: Axios
- **路由**: Vue Router

## 🚀 快速开始

### 使用 Docker (推荐)

1. **克隆项目**
```bash
git clone https://github.com/excniesNIED/AImagine.git
cd AImagine
```

2. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，修改必要的配置
```

3. **启动服务**
```bash
# 开发环境
docker-compose up -d

# 生产环境
docker-compose --profile production up -d
```

4. **访问应用**
- 前端: http://localhost:4321
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs
- Alist: http://localhost:5244

### 本地开发

#### 后端设置

1. **创建虚拟环境**
```bash
cd backend
conda create -n openaiga python=3.11 -y
conda activate openaiga
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件
```

4. **启动后端服务**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端设置

1. **安装依赖**
```bash
cd frontend
npm install
```

2. **启动开发服务器**
```bash
npm run dev
```

## 📖 详细文档

### 系统初始化

1. **创建管理员账号**
   - 访问 http://localhost:4321/register
   - 注册第一个用户后，手动在数据库中将 role 改为 'admin'

2. **配置 Alist**
   - 访问管理后台 (需要管理员权限)
   - 进入"系统设置" → "Alist 配置"
   - 填写 Alist URL、用户名/密码或 Token
   - 点击"测试连接"验证配置

### 用户手册

#### 普通用户功能

1. **上传图片**
   - 点击"上传"按钮
   - 拖拽或选择图片文件
   - 填写提示词、选择分类、模型、标签
   - 可选填写负面提示词和额外参数
   - 点击"上传作品"

2. **管理作品**
   - 在画廊中查看自己的作品
   - 点击图片查看详情
   - 可以编辑元数据信息
   - 可以删除作品（会同时删除 Alist 中的文件）

3. **版本控制**
   - 在图片详情页点击"基于此图创作"
   - 系统会预填充原有信息
   - 上传新图片后自动建立版本关联
   - 在"版本历史"中查看所有版本

4. **搜索和过滤**
   - 使用顶部搜索框进行全文搜索
   - 使用分类、模型下拉框过滤
   - 点击多个标签进行组合过滤

#### 管理员功能

1. **用户管理**
   - 查看所有用户列表
   - 修改用户角色（管理员/普通用户）
   - 禁用/启用用户账号

2. **分类管理**
   - 添加、编辑、删除分类
   - 合并分类（将一个分类合并到另一个）

3. **标签管理**
   - 添加、编辑、删除标签
   - 查看每个标签的使用数量
   - 合并标签、删除未使用的标签

4. **模型管理**
   - 管理 AI 模型列表
   - 添加、编辑、删除模型

5. **系统设置**
   - 配置 Alist 连接参数
   - 测试 Alist 连接状态
   - 查看系统统计信息

### API 文档

启动后端服务后，访问 http://localhost:8000/docs 查看完整的 API 文档。

主要 API 端点：

- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/register` - 用户注册
- `GET /api/v1/images` - 获取图片列表
- `POST /api/v1/images` - 上传图片
- `GET /api/v1/images/{id}` - 获取图片详情
- `PUT /api/v1/images/{id}` - 更新图片信息
- `DELETE /api/v1/images/{id}` - 删除图片
- `GET /api/v1/images/{id}/versions` - 获取版本历史
- `POST /api/v1/images/{id}/iterate` - 创建新版本

## 🔧 配置说明

### 环境变量

#### 后端配置

```env
# Database
DATABASE_URL=sqlite:///./gallery.db

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Alist/Openlist
ALIST_URL=http://localhost:5244
ALIST_USERNAME=admin
ALIST_PASSWORD=admin123
ALIST_TOKEN=your-alist-token
ALIST_UPLOAD_PATH=/gallery
```

#### 前端配置

前端通过 `.env` 文件配置 API 地址：

```env
PUBLIC_API_URL=http://localhost:8000
```

### Openlist 支持的存储后端

Openlist 支持多种存储后端，包括但不限于：
- 本地存储
- 阿里云 OSS
- 腾讯云 COS
- 百度网盘
- OneDrive
- Google Drive
- AWS S3
- 等等...

详细配置请参考 [Openlist 官方文档](https://doc.oplist.org)。

## 📦 部署指南

### 使用 Docker Compose (生产环境)

1. **准备服务器**
   - Ubuntu 20.04+ 或 CentOS 8+
   - 安装 Docker 和 Docker Compose
   - 确保端口 80、443 可用

2. **配置 SSL 证书**
   - 将证书文件放入 `ssl/` 目录
   - 修改 `nginx.conf` 中的证书路径

3. **启动服务**
```bash
docker-compose --profile production up -d
```

4. **配置反向代理**
Nginx 配置已包含在 `nginx.conf` 中，会自动处理：
- 前端路由
- API 代理
- 静态文件缓存
- SSL 终止

### 手动部署

#### 后端部署

1. **安装 Python 3.9+**

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置 Gunicorn**
```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

4. **设置 Systemd 服务**
```ini
[Unit]
Description=AI Gallery Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/backend
Environment=PATH=/path/to/venv/bin
ExecStart=/path/to/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

#### 前端部署

1. **构建生产版本**
```bash
npm run build
```

2. **使用 Nginx 或 Apache 托管 `dist/` 目录**

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📚 相关文档

- [开发指南](./DEVELOPMENT.md) - 详细的开发文档
- [故障排除](./TROUBLESHOOTING.md) - 常见问题解决方案

## 🚀 快速启动

### 使用初始化脚本（推荐）

**Windows**:
```bash
init.bat
```

**Linux/macOS**:
```bash
./init.sh
```

初始化脚本会自动：
- 创建虚拟环境
- 安装所有依赖
- 初始化数据库
- 创建默认数据
- 启动应用

### 使用 Python 脚本

```bash
python scripts/init.py
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代、快速的 Web 框架
- [Astro](https://astro.build/) - 面向内容的 Web 框架
- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [Tailwind CSS](https://tailwindcss.com/) - 实用优先的 CSS 框架
- [Openlist](https://doc.oplist.org) - 支持多存储的文件列表程序
- [PicList](https://github.com/Kuingsmile/PicList) - Openlist API 上传方法参考实现
- [picgo-plugin-alist](https://github.com/jinzhi0123/picgo-plugin-alist) - Openlist API 上传插件参考实现
- [UIverse - Loading Animation by dexter-st](https://uiverse.io/dexter-st/bright-lizard-8) - 开源前端加载动画组件
- [UIverse - Button Component by Pradeepsaranbishnoi](https://uiverse.io/Pradeepsaranbishnoi/heavy-dragonfly-92) - 开源前端按钮组件

---

⭐ 如果这个项目对你有帮助，请给它一个星标！