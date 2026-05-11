# Halo Blog v0.1.1 变更记录

> 更新日期：2026-05-11 | 作者：ArcaneCoreX-dev

---

## 🐛 Bug 修复

### 1. Dockerfile 构建失败
- **问题**：`pyproject.toml` 指定了 `readme = "README.md"`，但 Dockerfile 缓存层只复制了 `pyproject.toml`
- **修复**：`COPY pyproject.toml ./` → `COPY pyproject.toml README.md ./`
- **文件**：`Dockerfile` 第 11 行

### 2. 分类保存无反应
- **问题**：`admin.js` 中 `slug` 用 `const` 声明，但后续试图重新赋值，JS 报 `TypeError: Assignment to constant variable`
- **修复**：`const slug` → `let slug`
- **文件**：`src/static/js/admin.js` 第 340 行

### 3. 评论管理 500 错误
- **问题**：`admin_routes.py` 中 `len(c.replies)` 未处理 `None` 值
- **修复**：`len(c.replies)` → `len(c.replies) if c.replies else 0`
- **文件**：`src/api/admin_routes.py` 第 230 行

### 4. 文章详情页评论不显示
- **问题**：`blog_routes.py` 中 `_serialize_comment` 遍历 `c.replies` 时未处理 `None`
- **修复**：`for r in c.replies` → `for r in (c.replies or [])`
- **文件**：`src/api/blog_routes.py` 第 143 行

### 5. GitHub URL 错误
- **问题**：部分文件中 GitHub 地址使用了旧的 `Dreams-Zip`
- **修复**：全局替换为 `ArcaneCoreX-dev`
- **文件**：`README.md`、`docs/ZHIHU_ARTICLE.md`、`release/README.md`

---

## ✨ 新增功能

### 1. 标签选择功能
- **位置**：写文章编辑器
- **功能**：
  - 摘要下方新增标签选择区域
  - 点击标签选中/取消（选中变蓝色）
  - 保存时自动关联选中的标签
  - 编辑文章时自动加载已有标签
- **文件**：`src/static/js/admin.js`

### 2. 个人信息管理页面
- **位置**：后台左侧导航「👤 个人信息」
- **功能**：
  - 查看/修改显示名称、邮箱、头像 URL
  - 修改密码（旧密码验证 + 新密码确认 + 至少 6 位）
  - 修改密码后自动退出重新登录
- **API 端点**：
  - `GET /admin/api/profile` — 获取个人信息
  - `PUT /admin/api/profile` — 更新个人信息
  - `PUT /admin/api/profile/password` — 修改密码
- **文件**：`src/api/admin_routes.py`、`src/static/js/admin.js`、`src/templates/admin/dashboard.html`

### 3. 动态博客标题
- **功能**：前端标题自动显示管理员的显示名称 + " Blog"
- **实现**：模板渲染时从数据库读取管理员的 `display_name`
- **效果**：在个人信息中修改显示名称后，前台标题自动变化
- **文件**：`src/main.py`

### 4. 首页布局优化
- **改动**：
  - Hero 区域移至顶部全宽显示
  - 文章列表居中主区域
  - 分类和标签在右侧边栏
  - 移动端自动切换为单列
- **文件**：`src/templates/theme/index.html`、`src/static/css/style.css`

### 5. 错误提示增强
- **功能**：分类/标签创建失败时显示具体错误信息
- **改动**：添加 `try-catch` 和 API 错误响应解析
- **文件**：`src/static/js/admin.js`

---

## 📝 修改的文件清单

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| `Dockerfile` | 修复 | 构建时复制 README.md |
| `src/static/js/admin.js` | 修复+新增 | slug 修复、标签选择、个人信息、错误提示 |
| `src/api/admin_routes.py` | 修复+新增 | replies 空值检查、个人信息 API |
| `src/api/blog_routes.py` | 修复 | 评论序列化空值保护 |
| `src/main.py` | 新增 | 动态博客标题 |
| `src/templates/admin/dashboard.html` | 新增 | 个人信息导航项 |
| `src/templates/theme/index.html` | 修改 | 首页布局重构 |
| `src/static/css/style.css` | 修改 | 首页布局样式 |
| `README.md` | 更新 | 新增功能描述 |
| `CHANGELOG.md` | 更新 | v0.1.1 变更记录 |
| `CONTRIBUTING.md` | 更新 | 维护者信息 |
| `LICENSE` | 更新 | 版权信息 |
| `pyproject.toml` | 更新 | 项目元数据 |
| `.gitignore` | 新增 | Git 忽略规则 |
| `.github/workflows/ci.yml` | 新增 | CI/CD 配置 |
| `tests/conftest.py` | 新增 | 测试配置 |
| `tests/test_api.py` | 新增 | API 测试用例 |
| `docs/ZHIHU_ARTICLE.md` | 新增 | 知乎宣传文档 |
