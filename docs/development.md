# AI Gallery 开发指南

本文档介绍如何参与 AI Gallery 的开发。

## 开发环境设置

### 前置要求

- Python 3.9+
- Node.js 18+
- npm 或 pnpm
- Git
- VS Code（推荐）

### 克隆仓库

```bash
git clone https://github.com/yourusername/openai-gallery.git
cd openai-gallery
```

### 后端开发

1. 创建虚拟环境：
```bash
cd backend
conda create -n openaiga python=3.9
conda activate openaiga
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
```bash
cp .env.example .env
```

4. 初始化数据库：
```bash
# 创建数据库表
alembic upgrade head

# 初始化默认数据
python -m app.utils.init_db
```

5. 启动开发服务器：
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端 API 文档：http://localhost:8000/docs

### 前端开发

1. 安装依赖：
```bash
cd frontend
npm install
```

2. 启动开发服务器：
```bash
npm run dev
```

前端访问地址：http://localhost:4321

## 项目结构

```
openai-gallery/
├── backend/                 # Python FastAPI 后端
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据库模型
│   │   ├── schemas/        # Pydantic 模型
│   │   ├── services/       # 业务逻辑
│   │   └── utils/          # 工具函数
│   ├── migrations/         # 数据库迁移
│   └── tests/             # 测试文件
├── frontend/               # Astro + Vue 前端
│   ├── src/
│   │   ├── components/     # Vue 组件
│   │   ├── pages/          # Astro 页面
│   │   ├── layouts/        # 布局组件
│   │   ├── stores/         # Pinia 状态管理
│   │   └── styles/         # 样式文件
├── docs/                   # 文档
└── reference/             # 参考项目
```

## 代码规范

### Python 后端

使用 Black 进行代码格式化：

```bash
pip install black
black app/
```

使用 isort 整理导入：

```bash
pip install isort
isort app/
```

使用 flake8 进行代码检查：

```bash
pip install flake8
flake8 app/
```

### JavaScript 前端

使用 Prettier 进行代码格式化：

```bash
npm run format
```

使用 ESLint 进行代码检查：

```bash
npm run lint
```

## 添加新功能

### 1. 添加新的 API 端点

1. 在 `backend/app/schemas/` 中定义请求/响应模型
2. 在 `backend/app/api/v1/endpoints/` 中创建端点文件
3. 在 `backend/app/api/v1/api.py` 中注册路由
4. 编写测试用例

### 2. 添加新的前端页面

1. 在 `frontend/src/pages/` 中创建 Astro 页面
2. 在 `frontend/src/components/` 中创建 Vue 组件
3. 更新路由配置
4. 添加必要的状态管理

### 3. 数据库迁移

创建新的迁移文件：

```bash
alembic revision --autogenerate -m "描述变更"
```

应用迁移：

```bash
alembic upgrade head
```

## 测试

### 后端测试

运行所有测试：

```bash
pytest
```

运行特定测试：

```bash
pytest tests/test_auth.py
```

生成测试覆盖率报告：

```bash
pytest --cov=app tests/
```

### 前端测试

运行测试：

```bash
npm run test
```

## 调试

### 后端调试

使用 VS Code 调试器：

创建 `.vscode/launch.json`：

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/backend/.venv/bin/uvicorn",
            "args": [
                "app.main:app",
                "--reload",
                "--host",
                "0.0.0.0",
                "--port",
                "8000"
            ],
            "cwd": "${workspaceFolder}/backend",
            "console": "integratedTerminal"
        }
    ]
}
```

### 前端调试

使用浏览器开发者工具进行调试。Vue DevTools 扩展可以帮助调试 Vue 组件。

## 性能优化

### 后端优化

1. 使用数据库索引
2. 实现查询缓存
3. 使用连接池
4. 异步处理耗时任务

### 前端优化

1. 实现图片懒加载
2. 使用虚拟滚动
3. 优化 bundle 大小
4. 使用 CDN 加速静态资源

## 提交代码

1. 创建功能分支：
```bash
git checkout -b feature/new-feature
```

2. 提交代码：
```bash
git add .
git commit -m "feat: add new feature"
```

3. 推送分支：
```bash
git push origin feature/new-feature
```

4. 创建 Pull Request

### 提交信息规范

- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 添加测试
- `chore`: 其他更改

## 发布流程

1. 更新版本号
2. 更新 CHANGELOG.md
3. 创建 Git tag
4. 构建 Docker 镜像
5. 部署到生产环境

## 常见问题

### Q: 如何添加新的图片格式支持？

A: 在后端的 `alist_service.py` 中添加新的 MIME 类型检查。

### Q: 如何自定义主题？

A: 修改 `frontend/src/styles/global.css` 中的 Tailwind 配置。

### Q: 如何添加新的 AI 模型？

A: 管理员可以在管理后台添加，或通过数据库直接插入。

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 编写代码
4. 添加测试
5. 确保所有测试通过
6. 提交 Pull Request

感谢您的贡献！