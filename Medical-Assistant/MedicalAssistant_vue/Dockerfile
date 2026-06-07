# 构建前端
FROM node:20-alpine AS builder

WORKDIR /app

# 复制 package 文件
COPY package*.json ./

# 安装依赖
RUN npm ci --no-audit --no-fund

# 复制源代码
COPY . .

# 构建生产版本
RUN npm run build

# 生产阶段 - Nginx
FROM nginx:alpine

# 复制构建的前端文件到 Nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制自定义 Nginx 配置（如果需要）
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
