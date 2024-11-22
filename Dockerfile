# 使用官方的 Python 基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制当前目录的内容到工作目录
COPY . /app

# 安装依赖项
RUN pip install setuptools==57.5.0
RUN pip install pip==24.0
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口（如果需要）
EXPOSE 8000

# 运行命令（根据需要修改）
CMD ["python", "test.py"]