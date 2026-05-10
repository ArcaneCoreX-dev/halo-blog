# Contributing to Halo Blog

感谢你对 Halo Blog 项目的关注！

Maintainer: **ArcaneCoreX-dev**

## 如何贡献

### 报告 Bug

1. 在 [Issues](../../issues) 中搜索是否已有相同问题
2. 如果没有，创建新的 Issue
3. 请包含以下信息：
   - 操作系统和版本
   - Docker 版本
   - 复现步骤
   - 期望行为 vs 实际行为
   - 错误日志（如有）

### 提交功能建议

1. 在 [Issues](../../issues) 中创建 Feature Request
2. 详细描述你希望的功能
3. 说明使用场景

### 提交代码

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'feat: add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 创建 Pull Request

### Commit 规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
feat: 新功能
fix: 修复 Bug
docs: 文档更新
style: 代码格式（不影响功能）
refactor: 重构
test: 添加测试
chore: 构建/工具变更
```

### 开发环境

```bash
# 克隆仓库
git clone https://github.com/your-username/halo-blog.git
cd halo-blog

# 安装依赖
pip install -e ".[dev]"

# 启动开发服务器
uvicorn src.main:app --reload

# 运行测试
pytest

# 代码检查
ruff check .
ruff format .
```

## 行为准则

- 尊重每一位参与者
- 建设性地提出意见
- 接受批评和建议
- 专注于对社区最有利的事情

## 许可证

提交代码即表示你同意你的贡献将在 [MIT License](LICENSE) 下发布。
