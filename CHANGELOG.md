# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.1.1] - 2026-05-11 — ArcaneCoreX-dev

### Fixed
- **Dockerfile** — 构建时复制 `README.md`，修复 `pip install` 报错 `Readme file does not exist`
- **分类管理** — `const slug` 改为 `let slug`，修复 slug 自动生成时报 `Assignment to constant variable`
- **评论管理** — `len(c.replies)` 添加空值检查，修复 `NoneType` 导致的 500 错误
- **评论 API** — `_serialize_comment` 中 `c.replies` 添加 `or []` 空值保护
- **GitHub URL** — 全局替换 `Dreams-Zip` → `ArcaneCoreX-dev`

### Added
- **标签选择** — 写文章编辑器新增标签选择功能（点击选中/取消）
- **个人信息管理** — 后台新增「👤 个人信息」页面
  - 修改显示名称、邮箱、头像
  - 修改密码（旧密码验证 + 新密码确认）
- **动态博客标题** — 前端标题自动显示管理员的显示名称 + " Blog"
- **首页布局优化** — Hero 全宽 + 文章居中 + 侧边栏右侧
- **错误提示增强** — 分类/标签创建失败时显示具体错误信息
- **API 文档描述** — 为关键接口添加 `summary` 和 `description`

### Changed
- **首页布局** — 从单栏改为双栏（文章左侧 + 侧边栏右侧）
- **分类保存** — Slug 留空时自动生成，不再强制填写

## [0.1.0] - 2026-05-10 — ArcaneCoreX-dev

### Added
- 文章 CRUD 管理（Markdown 编辑器 + 实时预览）
- 分类系统（创建、编辑、删除）
- 标签系统（创建、删除、标签云）
- 评论系统（访客提交 + 管理员审核 + 嵌套回复）
- 友情链接管理（排序、可见性控制）
- 数据仪表盘（统计概览、最近文章/评论）
- JWT 认证的管理后台
- 归档页面（按年月分组）
- 响应式前端设计（移动端适配）
- 代码高亮（highlight.js）
- 文件上传功能
- Docker 容器化部署
- 一键启动/停止脚本（Windows）
- 完整项目文档和技术文档
