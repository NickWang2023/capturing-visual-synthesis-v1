# 更新日志

所有重要更改都将记录在此文件中。

格式基于[Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循[语义化版本](https://semver.org/lang/zh-CN/)。

## [V1.0.0] - 2026-07-03

### 新增
- **LLM服务模块** (`easymocap/llm/service.py`)
  - 智能算力调度
  - 参数自动生成
  - 智能错误诊断
  - 自然语言交互

- **VLM服务模块** (`easymocap/vlm/service.py`)
  - SAM分割模型集成
  - Grounding DINO检测
  - 人物分割功能
  - 关键点增强功能

- **性能优化模块** (`easymocap/performance/optimizer.py`)
  - 混合精度训练 (AMP)
  - 梯度累积
  - 缓存管理
  - GPU资源管理

- **API服务器** (`apps/api/server.py`)
  - FastAPI框架
  - OpenAPI文档
  - RESTful API
  - 健康检查接口

- **Docker容器化**
  - CPU版本Dockerfile
  - GPU版本Dockerfile (CUDA 12.1)
  - docker-compose编排配置

- **CI/CD自动化**
  - GitHub Actions流水线
  - 代码检查 (flake8, black, isort, mypy)
  - 单元测试
  - Docker构建和部署

- **测试框架**
  - pytest配置
  - 单元测试覆盖
  - 集成测试
  - 性能测试

- **配置文件**
  - pytest.ini - pytest配置
  - .coveragerc - 测试覆盖率配置
  - mypy.ini - 类型检查配置

### 改进
- **版本号更新**: setup.py 0.2.1 → 1.0.0
- **依赖版本升级**: 全面更新到最新稳定版本
- **类型注解**: 为核心函数添加Python类型注解
- **错误处理**: 完善异常处理和日志记录
- **代码质量**: 添加日志配置模块

### 修复
- **LLM模块依赖处理**: 添加openai可选导入
- **模块导入**: 修复__init__.py导入配置
- **gitignore**: 添加.bak文件排除规则

### 文档
- **README更新**: 添加版本信息和升级日志
- **升级指南**: UPGRADE_README.md
- **API文档**: FastAPI自动生成OpenAPI文档
- **HTML预览**: preview.html系统架构图

## [V0.2.1] - 2024-06-15

### 初始版本
- 多视角单人动作捕捉
- 互联网视频处理
- 镜面场景增强
- 多人动作捕捉
- 新视角合成 (Neural Body)

---

## 版本说明

- **主版本号 (MAJOR)**: 不兼容的API更改
- **次版本号 (MINOR)**: 以向后兼容的方式添加功能
- **修订号 (PATCH)**: 向后兼容的问题修复

## 链接

- [GitHub仓库](https://github.com/NickWang2023/capturing-visual-synthesis-v1)
- [升级指南](./upgrade/UPGRADE_README.md)
- [API文档](http://api-server:8000/docs)
