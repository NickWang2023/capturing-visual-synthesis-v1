# 🚀 快速开始指南

## 环境要求

- Python 3.10+
- CUDA 12.1+ (GPU支持)
- Docker & Docker Compose (容器化部署)

## 方式一：本地开发

### 1. 克隆项目

```bash
git clone https://github.com/NickWang2023/capturing-visual-synthesis-v1.git
cd capturing-visual-synthesis-v1
```

### 2. 创建虚拟环境

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入实际配置
```

### 5. 启动服务

```bash
# 启动API服务器
./scripts/start.sh api

# 或直接运行
python3 -m uvicorn apps.api.server:app --host 0.0.0.0 --port 8000 --reload
```

### 6. 访问服务

- API服务: http://localhost:8000
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## 方式二：Docker部署

### 1. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入实际配置
```

### 2. 启动服务

```bash
# 开发环境
docker-compose up -d

# 生产环境
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 带GPU支持
docker-compose --profile gpu up -d

# 带监控
docker-compose --profile monitor up -d
```

### 3. 查看服务状态

```bash
docker-compose ps
```

### 4. 访问服务

- API服务: http://localhost:8000
- Nginx: http://localhost:80
- Grafana: http://localhost:3000 (如果启用监控)
- Prometheus: http://localhost:9090 (如果启用监控)

## 方式三：一键部署

```bash
# 检查环境
./scripts/deploy.sh check

# 启动服务
./scripts/deploy.sh start

# 启动GPU服务
./scripts/deploy.sh start --gpu

# 启动监控
./scripts/deploy.sh start --gpu --monitor

# 查看状态
./scripts/deploy.sh status

# 查看日志
./scripts/deploy.sh logs

# 停止服务
./scripts/deploy.sh stop
```

## 常见问题

### 1. Python依赖安装失败

```bash
# 升级pip
pip install --upgrade pip setuptools wheel

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. CUDA相关错误

```bash
# 检查CUDA版本
nvidia-smi
nvcc --version

# 安装对应版本的PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 3. Docker构建失败

```bash
# 清理Docker缓存
docker system prune -a

# 重新构建
docker-compose build --no-cache
```

### 4. 端口被占用

```bash
# 查看端口占用
lsof -i :8000

# 杀死进程
kill -9 <PID>

# 或修改端口
export SERVER_PORT=8001
```

## 下一步

- 查看 [API文档](http://localhost:8000/docs)
- 阅读 [部署文档](./大模型支持下的动作捕捉与视觉合成系统V1.0-阿里云部署文档.md)
- 了解 [架构设计](./大模型支持下的动作捕捉与视觉合成系统建设方案_完整版.md)
- 贡献代码请参考 [贡献指南](./CONTRIBUTING.md)

## 获取帮助

- GitHub Issues: https://github.com/NickWang2023/capturing-visual-synthesis-v1/issues
- 文档: https://github.com/NickWang2023/capturing-visual-synthesis-v1#readme
