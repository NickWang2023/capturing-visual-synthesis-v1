# 大模型支持下的动作捕捉与视觉合成系统 V1.0
# 多阶段构建Dockerfile

# ==================== 构建阶段 ====================
FROM python:3.10-slim as builder

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# 创建虚拟环境
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# ==================== 运行阶段 ====================
FROM python:3.10-slim as runtime

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制虚拟环境
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 创建应用目录
WORKDIR /app

# 复制应用代码
COPY . .

# 创建必要目录
RUN mkdir -p /app/logs /app/data /app/output /app/models

# 设置权限
RUN chmod +x /app/scripts/*.sh 2>/dev/null || true

# 暴露端口
EXPOSE 8000 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["python", "-m", "uvicorn", "apps.mocap.service:app", "--host", "0.0.0.0", "--port", "8000"]
