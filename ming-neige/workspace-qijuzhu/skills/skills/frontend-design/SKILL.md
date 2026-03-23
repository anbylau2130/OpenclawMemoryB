---
name: frontend-design
description: 前端设计指南与最佳实践。涵盖UI/UX设计、组件设计、响应式布局、性能优化、可访问性等。适用于创建用户界面、优化用户体验、前端架构设计。
---

# Frontend Design - 前端设计指南

## 概述

提供前端设计的完整指南，从 UI/UX 设计到性能优化，确保创建高质量的用户界面。

---

## 设计原则

### 1. 以用户为中心
- 🎯 **可用性优先** - 界面易于使用和理解
- ♿ **可访问性** - 支持所有用户（包括残障用户）
- 📱 **响应式** - 适配所有设备和屏幕尺寸
- ⚡ **性能** - 快速加载和响应

### 2. 设计一致性
- 🎨 **视觉一致** - 统一的颜色、字体、间距
- 🧩 **组件复用** - 使用设计系统和组件库
- 📐 **布局规范** - 遵循栅格系统和排版规则
- 🔤 **排版层级** - 清晰的信息层级

### 3. 简洁明了
- ✂️ **减少认知负担** - 每屏只显示必要信息
- 🎪 **渐进式披露** - 逐步展示复杂功能
- 🖼️ **留白** - 合理使用空白空间
- 🔍 **视觉焦点** - 引导用户注意力

---

## UI 设计

### 颜色系统

#### 主色调
```css
/* 主色 */
--primary-50: #E3F2FD;
--primary-100: #BBDEFB;
--primary-500: #2196F3;  /* 主色调 */
--primary-700: #1976D2;  /* 悬停状态 */
--primary-900: #0D47A1;  /* 按下状态 */

/* 中性色 */
--gray-50: #FAFAFA;
--gray-100: #F5F5F5;
--gray-900: #212121;

/* 功能色 */
--success: #4CAF50;
--warning: #FF9800;
--error: #F44336;
```

#### 颜色对比
- ✅ **WCAG AA 标准** - 对比度 ≥ 4.5:1（正常文本）
- ✅ **WCAG AAA 标准** - 对比度 ≥ 7:1（大文本）
- ❌ 避免低对比度（如浅灰色文本）

### 排版

#### 字体系统
```css
/* 字体族 */
--font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
--font-mono: 'SF Mono', 'Monaco', 'Consolas', monospace;

/* 字号 */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */

/* 行高 */
--leading-tight: 1.25;
--leading-normal: 1.5;
--leading-relaxed: 1.75;
```

#### 间距系统
```css
/* 基于 4px 的间距系统 */
--space-1: 0.25rem;  /* 4px */
--space-2: 0.5rem;   /* 8px */
--space-3: 0.75rem;  /* 12px */
--space-4: 1rem;     /* 16px */
--space-6: 1.5rem;   /* 24px */
--space-8: 2rem;     /* 32px */
```

---

## 组件设计

### 1. 按钮组件

#### 类型
```tsx
// 主要按钮
<Button variant="primary">主要操作</Button>

// 次要按钮
<Button variant="secondary">次要操作</Button>

// 文本按钮
<Button variant="text">文本按钮</Button>

// 图标按钮
<Button variant="icon"><Icon /></Button>
```

#### 状态
```tsx
// 默认
<Button>默认</Button>

// 悬停
<Button className="hover">悬停</Button>

// 聚焦
<Button className="focus">聚焦</Button>

// 禁用
<Button disabled>禁用</Button>

// 加载中
<Button loading>加载中</Button>
```

### 2. 表单组件

#### 输入框
```tsx
<Input
  label="用户名"
  placeholder="请输入用户名"
  error="用户名不能为空"
  required
/>
```

#### 下拉选择
```tsx
<Select
  label="国家"
  options={[
    { value: 'cn', label: '中国' },
    { value: 'us', label: '美国' }
  ]}
/>
```

### 3. 卡片组件

```tsx
<Card>
  <CardHeader>
    <CardTitle>标题</CardTitle>
    <CardDescription>描述</CardDescription>
  </CardHeader>
  <CardContent>
    内容
  </CardContent>
  <CardFooter>
    <Button>操作</Button>
  </CardFooter>
</Card>
```

---

## 响应式设计

### 断点系统

```css
/* 移动设备 */
@media (min-width: 640px) { /* sm */ }

/* 平板 */
@media (min-width: 768px) { /* md */ }

/* 桌面 */
@media (min-width: 1024px) { /* lg */ }

/* 大屏 */
@media (min-width: 1280px) { /* xl */ }
```

### 栅格系统

```tsx
// 12 列栅格
<Grid cols={12}>
  <GridItem colSpan={4}>1/3 宽度</GridItem>
  <GridItem colSpan={8}>2/3 宽度</GridItem>
</Grid>

// 响应式栅格
<Grid cols={12}>
  <GridItem colSpan={12} md={6} lg={4}>
    移动端全宽，平板半宽，桌面 1/3 宽
  </GridItem>
</Grid>
```

---

## 性能优化

### 1. 图片优化

#### 格式选择
- ✅ **WebP** - 最佳压缩比
- ✅ **AVIF** - 新一代格式
- ✅ **PNG** - 需要透明度时
- ✅ **JPEG** - 照片类图片

#### 懒加载
```tsx
<img 
  src="placeholder.jpg"
  data-src="real-image.jpg"
  loading="lazy"
  alt="描述"
/>
```

#### 响应式图片
```tsx
<picture>
  <source media="(min-width: 1024px)" srcSet="large.webp" />
  <source media="(min-width: 768px)" srcSet="medium.webp" />
  <img src="small.webp" alt="描述" />
</picture>
```

### 2. 代码分割

```tsx
// 动态导入
const HeavyComponent = lazy(() => import('./HeavyComponent'));

// 使用
<Suspense fallback={<Loading />}>
  <HeavyComponent />
</Suspense>
```

### 3. 缓存策略

```typescript
// Service Worker 缓存
const cacheVersion = 'v1';

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
```

---

## 可访问性（A11Y）

### 1. 语义化 HTML

```tsx
// ✅ 好的实践
<nav>
  <ul>
    <li><a href="/">首页</a></li>
    <li><a href="/about">关于</a></li>
  </ul>
</nav>

// ❌ 避免
<div onClick={navigate}>首页</div>
```

### 2. ARIA 标签

```tsx
// 按钮
<button aria-label="关闭菜单">
  <Icon name="close" />
</button>

// 表单
<input
  aria-label="搜索"
  aria-describedby="search-hint"
/>
<span id="search-hint">输入关键词搜索</span>

// 模态框
<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="dialog-title"
>
  <h2 id="dialog-title">标题</h2>
</div>
```

### 3. 键盘导航

```tsx
// 焦点管理
<button
  tabIndex={0}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      handleClick();
    }
  }}
>
  按钮
</button>
```

---

## 设计系统

### 组件库推荐

| 框架 | 组件库 | 特点 |
|------|--------|------|
| **React** | Ant Design | 企业级，中文友好 |
| **React** | Material-UI | Material Design |
| **React** | Chakra UI | 简洁，可定制 |
| **Vue** | Element Plus | 企业级，中文友好 |
| **Vue** | Vuetify | Material Design |
| **通用** | Tailwind UI | 实用工具优先 |

### 设计工具

| 工具 | 用途 | 链接 |
|------|------|------|
| **Figma** | UI 设计 | figma.com |
| **Sketch** | UI 设计（Mac）| sketch.com |
| **Adobe XD** | UI 设计 | adobe.com/xd |
| **Framer** | 交互原型 | framer.com |

---

## 最佳实践

### 1. 移动优先
```css
/* 默认：移动端样式 */
.container {
  padding: 1rem;
}

/* 平板及以上 */
@media (min-width: 768px) {
  .container {
    padding: 2rem;
  }
}
```

### 2. 性能预算
- ✅ **首次加载** < 3s（3G 网络）
- ✅ **首次有意义渲染** < 1.5s
- ✅ **交互时间** < 3.5s
- ✅ **bundle 大小** < 200KB（gzip）

### 3. 设计审查清单
- [ ] 颜色对比度符合 WCAG AA
- [ ] 所有交互元素可键盘访问
- [ ] 图片有 alt 属性
- [ ] 表单有 label
- [ ] 响应式在所有断点测试
- [ ] 性能指标达标

---

## 常见问题

### Q: 如何选择组件库？
A: 根据项目需求：
- 企业级后台 → Ant Design / Element Plus
- 移动端 H5 → Vant / Ant Design Mobile
- 设计定制 → Tailwind UI / Chakra UI
- 快速原型 → Material-UI / Vuetify

### Q: 响应式设计的原则？
A: 
1. 移动优先
2. 使用相对单位（rem, %, vw/vh）
3. 测试所有断点
4. 图片自适应

### Q: 如何优化性能？
A:
1. 代码分割
2. 图片优化
3. 缓存策略
4. 懒加载
5. CDN 加速

---

## 参考资料

- **Material Design:** material.io
- **Apple HIG:** developer.apple.com/design
- **WCAG 2.1:** w3.org/WAI/WCAG21
- **Tailwind CSS:** tailwindcss.com

---

_更新时间: 2026-03-23_
_版本: 1.0_
