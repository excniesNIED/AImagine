# 海浪泡沫配色方案使用指南

本项目已应用海浪泡沫配色方案，以下是配色的详细说明和使用指南。

## 配色定义

### 主色调 (Primary)
- **主色**: `#93A5ED` (蓝紫色)
- **用途**: 主要按钮、链接、图标、重要标题
- **Tailwind类**: `primary-500`, `bg-primary-500`, `text-primary-500`
- **变体**:
  - `primary-50`: `#F5FFFA` (薄荷白)
  - `primary-100`: `#D9F1FA` (浅天蓝)
  - `primary-200`: `#CDDDFA` (点缀背景)
  - `primary-300` - `primary-500`: `#93A5ED` (主色)
  - `primary-600`: `#7A8ED9` (深一点)
  - `primary-700`: `#6277C5` (更深)
  - `primary-800`: `#4A60B0` (暗色)
  - `primary-900`: `#32499C` (最深)

### 辅助色 (Secondary)
- **辅助色**: `#9FBFBC` (灰绿色)
- **用途**: 次要按钮、标签、信息提示框、次要图标
- **Tailwind类**: `secondary-300`, `bg-secondary-300`, `text-secondary-300`
- **变体**:
  - `secondary-50`: `#F0F5F4`
  - `secondary-100`: `#E0ECEB`
  - `secondary-200`: `#D0E3E2`
  - `secondary-300` - `secondary-500`: `#9FBFBC`
  - `secondary-600`: `#7FA8A5`
  - `secondary-700`: `#5F918E`
  - `secondary-800`: `#3F7A77`
  - `secondary-900`: `#1F6360`

### 背景色 (Background)
- **纯白背景**: `#FFFFFF` - `background-primary` 或 `bg-white`
- **极浅灰背景**: `#F8F9FA` - `background-secondary` 或 `bg-gray-50`
- **浅天蓝背景**: `#D9F1FA` - `background-light`
- **点缀背景**: `#CDDDFA` - `background-accent`
- **薄荷白背景**: `#F5FFFA` - `background-mint`

### 文本色 (Text)
- **主要文本**: `#212529` (深灰) - `text-text-primary`
- **次要文本**: `#6C757D` (中灰) - `text-text-secondary`

### 边框色 (Border)
- **浅灰边框**: `#E9ECEF` - `border-border-light`

### 功能性颜色 (Functional)
- **成功**: `#28A745` - `bg-success`, `text-success`
- **错误/危险**: `#DC3545` - `bg-danger`, `text-danger`
- **警告**: `#FFC107` - `bg-warning`, `text-warning` (警告文本使用深色)

## 组件样式类

### 按钮
```css
/* 主要按钮 */
.btn-primary
- 白色文字，主色背景
- hover时背景变深
- 用于主要操作

/* 次要按钮 */
.btn-secondary
- 次要文本，白色背景，辅助色边框
- hover时背景变浅
- 用于次要操作

/* 成功按钮 */
.btn-success
- 白色文字，成功色背景
- 用于确认操作

/* 危险按钮 */
.btn-danger
- 白色文字，危险色背景
- 用于删除等危险操作

/* 警告按钮 */
.btn-warning
- 深色文字，警告色背景
- 用于需要注意的操作
```

### 卡片
```css
.card
- 白色背景（暗色模式下为深灰）
- 浅灰边框
- 圆角和阴影
```

### 容器
```css
.container
- 最大宽度7xl
- 响应式内边距
```

## 暗色模式支持

所有颜色都已配置暗色模式变体：
- 使用 `dark:` 前缀来指定暗色模式样式
- 主色和辅助色在暗色模式下使用较浅的变体（如 `dark:text-primary-300`）
- 背景在暗色模式下使用深灰色系
- 边框在暗色模式下使用深灰色

## 实际应用示例

### 页面背景
```html
<body class="bg-background-mint dark:bg-gray-900">
```

### 导航链接
```html
<a class="text-text-primary dark:text-gray-200 hover:text-primary-500">
```

### 输入框
```html
<input class="border border-border-light dark:border-gray-600 
              bg-white dark:bg-gray-800 
              focus:ring-2 focus:ring-primary-500">
```

### 标签
```html
<!-- 选中的标签 -->
<button class="bg-primary-500 text-white">

<!-- 未选中的标签 -->
<button class="bg-background-accent dark:bg-gray-700 
               text-text-primary dark:text-gray-300">
```

### Toast通知
```html
<!-- 成功 -->
<div class="bg-success text-white">

<!-- 错误 -->
<div class="bg-danger text-white">

<!-- 信息 -->
<div class="bg-primary-500 text-white">

<!-- 警告 -->
<div class="bg-warning text-gray-900">
```

## 注意事项

1. 优先使用语义化的颜色类（如 `text-text-primary`）而不是直接的颜色值
2. 所有交互元素都应该有 hover 状态
3. 确保文本和背景之间有足够的对比度
4. 暗色模式下注意颜色的可读性
5. 使用 `transition-colors` 类来添加颜色过渡动画

## 配色文件位置

- **Tailwind配置**: `frontend/tailwind.config.mjs`
- **全局CSS**: `frontend/src/styles/global.css`
- **主题存储**: `frontend/src/stores/theme.ts`

## 更新日期

2025-10-07

