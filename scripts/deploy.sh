#!/bin/bash

# MyPress 一键部署脚本
# 适用于 x86_64 Docker 环境

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  MyPress 一键部署脚本${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker未安装${NC}"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}错误: docker-compose未安装${NC}"
    echo "请先安装 docker-compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# 检查.env文件
if [ ! -f .env ]; then
    echo -e "${YELLOW}创建环境配置文件...${NC}"
    cp .env.example .env
    
    # 生成随机SECRET_KEY
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(50))")
    sed -i "s/your-secret-key-here-change-in-production/$SECRET_KEY/" .env
    
    # 生成随机数据库密码
    DB_PASSWORD=$(python3 -c "import secrets; print(secrets.token_hex(16))")
    sed -i "s/change-this-password-in-production/$DB_PASSWORD/" .env
    
    echo -e "${GREEN}环境配置文件已创建: .env${NC}"
    echo -e "${YELLOW}请编辑 .env 文件配置您的参数${NC}"
    echo ""
fi

# 创建必要目录
echo -e "${YELLOW}创建数据目录...${NC}"
mkdir -p data/media
mkdir -p data/db

# 检查端口是否被占用
PORT=$(grep "^MYPRESS_PORT=" .env | cut -d'=' -f2)
if [ -z "$PORT" ]; then
    PORT=8000
fi

if netstat -tuln 2>/dev/null | grep -q ":$PORT "; then
    echo -e "${RED}错误: 端口 $PORT 已被占用${NC}"
    echo "请修改 .env 文件中的 MYPRESS_PORT"
    exit 1
fi

# 构建Docker镜像
echo -e "${YELLOW}构建Docker镜像...${NC}"
docker-compose build

# 启动服务
echo -e "${YELLOW}启动服务...${NC}"
docker-compose up -d

# 等待服务启动
echo -e "${YELLOW}等待服务启动...${NC}"
sleep 10

# 检查服务状态
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  部署成功!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "访问地址: ${GREEN}http://localhost:$PORT${NC}"
    echo -e "管理后台: ${GREEN}http://localhost:$PORT/admin/${NC}"
    echo ""
    echo "常用命令:"
    echo "  查看日志: docker-compose logs -f"
    echo "  停止服务: docker-compose down"
    echo "  重启服务: docker-compose restart"
    echo ""
else
    echo -e "${RED}部署失败，请检查日志: docker-compose logs${NC}"
    exit 1
fi
