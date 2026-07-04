# 贡献指南

感谢您对《大模型支持下的动作捕捉与视觉合成系统》项目的关注！

## 📋 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [开发环境](#开发环境)
- [代码规范](#代码规范)
- [提交规范](#提交规范)
- [Issue规范](#issue规范)
- [PR规范](#pr规范)

## 行为准则

本项目采用 [Contributor Covenant](https://www.contributor-covenant.org/zh-cn/version/2/0/code_of_conduct/) 行为准则。参与本项目即表示您同意遵守此准则。

## 如何贡献

### 报告Bug

1. 使用 [GitHub Issues](https://github.com/NickWang2023/capturing-visual-synthesis-v1/issues) 报告Bug
2. 使用Bug报告模板
3. 提供详细的复现步骤
4. 附上错误日志和截图

### 提交功能请求

1. 使用 [GitHub Issues](https://github.com/NickWang2023/capturing-visual-synthesis-v1/issues) 提交功能请求
2. 使用功能请求模板
3. 详细描述使用场景
4. 说明预期行为

### 提交代码

1. Fork 项目
2. 创建功能分支
3. 提交代码
4. 创建 Pull Request

## 开发环境

### 环境要求

- Python 3.10+
- CUDA 12.1+ (GPU支持)
- Git

### 安装步骤

```bash
# 1. Fork并克隆项目
git clone https://github.com/YOUR_USERNAME/capturing-visual-synthesis-v1.git
cd capturing-visual-synthesis-v1

# 2. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt
pip install -e ".[dev]"

# 4. 运行测试
pytest tests/ -v
```

### 开发工具

```bash
# 代码格式化
black .
isort .

# 代码检查
flake8 .
mypy .

# 运行测试
pytest tests/ -v --cov=easymocap
```

## 代码规范

### Python代码规范

- 遵循 [PEP 8](https://peps.python.org/pep-0008/) 代码规范
- 使用 [Black](https://github.com/psf/black) 进行代码格式化
- 使用 [isort](https://pycqa.github.io/isort/) 进行导入排序
- 使用 [mypy](https://mypy.readthedocs.io/) 进行类型检查

### 命名规范

- **类名**: `PascalCase` (如 `LLMService`, `VLMService`)
- **函数名**: `snake_case` (如 `analyze_task_complexity`)
- **变量名**: `snake_case` (如 `video_info`)
- **常量名**: `UPPER_SNAKE_CASE` (如 `OPENAI_AVAILABLE`)
- **私有成员**: `_snake_case` (如 `_init_models`)

### 文档规范

- 所有公共函数必须有docstring
- 使用Google风格的docstring格式
- 类型注解必须完整

```python
def analyze_task_complexity(
    self,
    video_info: Dict[str, Any]
) -> TaskComplexity:
    """
    使用LLM分析任务复杂度
    
    Args:
        video_info: 视频信息字典
            - duration: 视频时长（秒）
            - resolution: 分辨率
            - fps: 帧率
    
    Returns:
        TaskComplexity对象
    
    Raises:
        RuntimeError: 分析失败时抛出
    """
    pass
```

## 提交规范

### 提交消息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 类型 (type)

- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具相关

### 示例

```
feat(llm): 新增LLM服务模块

- 实现智能算力调度
- 实现参数自动生成
- 实现错误诊断

Closes #5
```

## Issue规范

### Bug报告模板

```markdown
## Bug描述
简要描述Bug

## 复现步骤
1. 执行 '...'
2. 点击 '...'
3. 看到错误

## 预期行为
描述预期行为

## 实际行为
描述实际行为

## 环境信息
- OS: [如 macOS 13.0]
- Python: [如 3.10.0]
- CUDA: [如 12.1]

## 错误日志
```
粘贴错误日志
```

## 截图
如果适用，添加截图
```

### 功能请求模板

```markdown
## 功能描述
简要描述功能

## 使用场景
描述使用场景

## 预期行为
描述预期行为

## 替代方案
描述替代方案

## 附加信息
其他相关信息
```

## PR规范

### PR标题格式

```
<type>(<scope>): <description>
```

### PR描述模板

```markdown
## 变更描述
简要描述变更

## 变更类型
- [ ] Bug修复
- [ ] 新功能
- [ ] 文档更新
- [ ] 重构
- [ ] 性能优化
- [ ] 测试相关

## 测试
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 手动测试通过

## 相关Issue
Closes #123

## 截图
如果适用，添加截图

## 检查清单
- [ ] 代码符合规范
- [ ] 已添加测试
- [ ] 已更新文档
- [ ] 已更新CHANGELOG
```

## 代码审查

### 审查要点

1. **功能正确性**: 代码是否实现了预期功能
2. **代码质量**: 是否符合代码规范
3. **测试覆盖**: 是否有足够的测试
4. **文档完整**: 是否更新了相关文档
5. **性能影响**: 是否有性能问题
6. **安全性**: 是否有安全漏洞

### 审查流程

1. 提交PR
2. 自动化检查 (CI/CD)
3. 代码审查
4. 修改和完善
5. 合并

## 版本发布

### 版本号规则

采用 [语义化版本](https://semver.org/lang/zh-CN/) 规则：

- **主版本号 (MAJOR)**: 不兼容的API更改
- **次版本号 (MINOR)**: 以向后兼容的方式添加功能
- **修订号 (PATCH)**: 向后兼容的问题修复

### 发布流程

1. 更新版本号
2. 更新CHANGELOG
3. 创建Release Tag
4. 自动构建和发布
5. 部署到生产环境

## 联系方式

- **Issues**: [GitHub Issues](https://github.com/NickWang2023/capturing-visual-synthesis-v1/issues)
- **讨论**: [GitHub Discussions](https://github.com/NickWang2023/capturing-visual-synthesis-v1/discussions)

## 致谢

感谢所有贡献者对项目的支持！

---

**最后更新**: 2026-07-03
**维护者**: 致业电子
