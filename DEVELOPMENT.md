# 开发指南

本文档为想要参与 AI Gallery 项目的开发者提供详细的开发指南。

## 目录

- [开发环境设置](#开发环境设置)
- [项目结构](#项目结构)
- [后端开发](#后端开发)
- [前端开发](#前端开发)
- [数据库](#数据库)
- [API 开发](#api-开发)
- [测试](#测试)
- [代码规范](#代码规范)
- [贡献流程](#贡献流程)

## 开发环境设置

### 前置要求

- Python 3.9+
- Node.js 18+
- Git
- Docker (可选)

### 快速设置

1. **克隆项目**
```bash
git clone https://github.com/yourusername/AImagine.git
cd AImagine
```

2. **使用初始化脚本**
```bash
# Windows
init.bat

# Linux/macOS
./init.sh
```

3. **手动设置（如果初始化脚本失败）**

#### 后端设置
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

#### 前端设置
```bash
cd frontend
npm install
```

## 项目结构

```
AImagine/
├── backend/                 # Python FastAPI 后端
│   ├── app/
│   │   ├── api/            # API 路由
│   │   │   └── v1/        # API v1 版本
│   │   ├── core/          # 核心配置
│   │   ├── models/        # 数据库模型
│   │   ├── schemas/       # Pydantic 模式
│   │   ├── services/      # 业务逻辑
│   │   └── main.py        # 应用入口
│   ├── requirements.txt   # Python 依赖
│   └── Dockerfile        # Docker 配置
├── frontend/              # Astro + Vue 前端
│   ├── src/
│   │   ├── components/   # Vue 组件
│   │   ├── pages/        # Astro 页面
│   │   ├── stores/       # Pinia 状态管理
│   │   └── layouts/      # 页面布局
│   ├── package.json      # Node.js 依赖
│   └── Dockerfile       # Docker 配置
├── docs/                 # 文档
├── scripts/              # 辅助脚本
├── docker-compose.yml    # Docker Compose 配置
├── nginx.conf           # Nginx 配置
└── README.md            # 项目说明
```

## 后端开发

### 添加新的 API 端点

1. 在 `backend/app/api/v1/endpoints/` 下创建新的路由文件
2. 在 `backend/app/api/v1/api.py` 中注册路由
3. 在 `backend/app/schemas/` 中定义请求/响应模式
4. 在 `backend/app/services/` 中实现业务逻辑

示例：创建新的用户统计 API

```python
# backend/app/api/v1/endpoints/stats.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_admin_user

router = APIRouter()

@router.get("/user-stats")
async def get_user_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    # 实现统计逻辑
    pass
```

### 数据库操作

使用 SQLAlchemy ORM 进行数据库操作：

```python
# 查询
images = db.query(Image).filter(Image.owner_id == user_id).all()

# 创建
new_image = Image(prompt="test", owner_id=user_id)
db.add(new_image)
db.commit()

# 更新
image.prompt = "new prompt"
db.commit()

# 删除
db.delete(image)
db.commit()
```

### 认证和授权

使用 JWT 进行认证：

```python
from app.api.deps import get_current_user, get_current_admin_user

@router.get("/protected")
async def protected_route(
    current_user: User = Depends(get_current_user)
):
    # 只有认证用户可以访问
    pass

@router.get("/admin")
async def admin_route(
    admin_user: User = Depends(get_current_admin_user)
):
    # 只有管理员可以访问
    pass
```

## 前端开发

### 组件开发

使用 Vue 3 Composition API 创建组件：

```vue
<template>
  <div class="component">
    {{ message }}
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

const message = ref('Hello World');

onMounted(() => {
  // 组件挂载后的逻辑
});
</script>

<style scoped>
.component {
  /* 样式 */
}
</style>
```

### 状态管理

使用 Pinia 进行状态管理：

```typescript
// stores/example.ts
import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useExampleStore = defineStore('example', () => {
  const count = ref(0);

  const increment = () => {
    count.value++;
  };

  return { count, increment };
});
```

### API 调用

使用 Axios 进行 API 调用：

```typescript
import axios from 'axios';

// 获取图片列表
const fetchImages = async () => {
  try {
    const response = await axios.get('/api/v1/images');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch images:', error);
    throw error;
  }
};
```

## 数据库

### 添加新模型

1. 在 `backend/app/models/` 中创建模型文件
2. 继承 `Base` 类
3. 定义字段和关系

```python
# backend/app/models/example.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class Example(Base):
    __tablename__ = "examples"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

    # 关系
    images = relationship("Image", back_populates="example")
```

### 数据库迁移

创建迁移脚本：

```bash
cd scripts
python migrate.py
```

## API 开发

### RESTful API 设计原则

- 使用正确的 HTTP 方法（GET, POST, PUT, DELETE）
- 使用复数名词作为资源名
- 使用 HTTP 状态码
- 实现分页
- 使用查询参数进行过滤和排序

示例：

```
GET    /api/v1/images          # 获取图片列表
POST   /api/v1/images          # 创建新图片
GET    /api/v1/images/{id}     # 获取单个图片
PUT    /api/v1/images/{id}     # 更新图片
DELETE /api/v1/images/{id}     # 删除图片
```

### 错误处理

```python
from fastapi import HTTPException

# 400 Bad Request
raise HTTPException(status_code=400, detail="Invalid input")

# 401 Unauthorized
raise HTTPException(status_code=401, detail="Not authenticated")

# 403 Forbidden
raise HTTPException(status_code=403, detail="Not authorized")

# 404 Not Found
raise HTTPException(status_code=404, detail="Resource not found")
```

## 测试

### 后端测试

使用 pytest 进行测试：

```python
# tests/test_images.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_images():
    response = client.get("/api/v1/images")
    assert response.status_code == 200
    assert "items" in response.json()
```

### 前端测试

使用 Vitest 进行测试：

```typescript
// tests/example.test.ts
import { test, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import ExampleComponent from '../src/components/ExampleComponent.vue';

test('renders component', () => {
  const wrapper = mount(ExampleComponent);
  expect(wrapper.text()).toContain('Hello World');
});
```

## 代码规范

### Python 代码规范

- 遵循 PEP 8
- 使用 Black 进行代码格式化
- 使用 isort 进行导入排序
- 使用 flake8 进行代码检查

```bash
# 安装开发依赖
pip install black isort flake8

# 格式化代码
black .
isort .

# 检查代码
flake8 .
```

### TypeScript/JavaScript 代码规范

- 使用 ESLint + Prettier
- 使用 TypeScript 严格模式
- 组件使用 PascalCase 命名
- 文件使用 kebab-case 命名

```bash
# 安装开发依赖
npm install -D eslint prettier

# 格式化代码
npm run format

# 检查代码
npm run lint
```

### 提交信息规范

使用约定式提交格式：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

类型：
- feat: 新功能
- fix: 修复
- docs: 文档
- style: 格式
- refactor: 重构
- test: 测试
- chore: 构建/工具

示例：
```
feat(auth): add JWT refresh token support

- Add refresh token endpoint
- Update token validation logic
- Add unit tests

Closes #123
```

## 贡献流程

1. Fork 项目
2. 创建功能分支
```bash
git checkout -b feature/your-feature
```

3. 提交更改
```bash
git add .
git commit -m "feat: add your feature"
```

4. 推送分支
```bash
git push origin feature/your-feature
```

5. 创建 Pull Request

### PR 要求

- 包含清晰的描述
- 通过所有测试
- 代码格式化
- 更新相关文档
- 添加必要的测试

## 有用的命令

### 后端开发

```bash
# 激活虚拟环境
source venv/bin/activate

# 启动开发服务器
uvicorn app.main:app --reload

# 运行测试
pytest

# 代码格式化
black .
isort .

# 检查代码
flake8 .
```

### 前端开发

```bash
# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 运行测试
npm test

# 代码格式化
npm run format

# 代码检查
npm run lint
```

### Docker

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重新构建
docker-compose up -d --build
```

## 常见问题

### Q: 如何添加新的数据库字段？
A: 修改模型文件，然后运行迁移脚本。

### Q: 如何自定义 Alist 配置？
A: 在管理后台的系统设置中配置，或修改 `.env` 文件。

### Q: 如何添加新的存储后端？
A: 参考 Alist 官方文档配置相应的存储后端。

### Q: 如何部署到生产环境？
A: 使用 `docker-compose --profile production up -d` 命令。

## 获取帮助

- 查看 [API 文档](http://localhost:8000/docs)
- 提交 [Issue](https://github.com/yourusername/AImagine/issues)
- 查看 [Alist 文档](https://alist.nn.ci/)