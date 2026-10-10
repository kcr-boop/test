# 微信云托管容器：构建上下文为仓库根目录
FROM python:3.12-slim
WORKDIR /srv
COPY engine /srv/engine
COPY server /srv/server
RUN pip install --no-cache-dir /srv/engine "fastapi>=0.110" "uvicorn[standard]>=0.29"
WORKDIR /srv/server
EXPOSE 80
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
