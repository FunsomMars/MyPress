#!/bin/bash

# MyPress 一键部署脚本
# 适用于 x86_64 Docker 环境

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  MyPress 一键部署脚本${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker 未安装${NC}"
    echo "安装命令: curl -fsSL https://get.docker.com | sh"
    exit 1
fi

if ! docker compose version &> /dev/null && ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}错误: Docker Compose 未安装${NC}"
    echo "请安装 Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}[1/6] Docker 环境检查通过${NC}"

# 检查 .env 文件
if [ ! -f .env ]; then
    echo -e "${YELLOW}[2/6] 创建环境配置文件...${NC}"
    cp .env.example .env

    # 生成随机 SECRET_KEY
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(50))" 2>/dev/null || openssl rand -hex 50)
    sed -i "s/your-secret-key-here-change-in-production/$SECRET_KEY/" .env

    # 生成随机数据库密码
    DB_PASSWORD=$(python3 -c "import secrets; print(secrets.token_hex(16))" 2>/dev/null || openssl rand -hex 16)
    sed -i "s/change-this-password-in-production/$DB_PASSWORD/" .env

    echo -e "${GREEN}  .env 已创建（SECRET_KEY 和数据库密码已自动生成）${NC}"
else
    echo -e "${GREEN}[2/6] .env 文件已存在，跳过${NC}"
fi

# 创建必要目录
echo -e "${YELLOW}[3/6] 创建数据目录...${NC}"
mkdir -p data/media
mkdir -p /var/www/static
mkdir -p /var/www/media/uploads

# 检查端口
PORT=$(grep "^MYPRESS_PORT=" .env 2>/dev/null | cut -d'=' -f2)
PORT=${PORT:-8000}

if command -v ss &> /dev/null; then
    if ss -tlnp 2>/dev/null | grep -q ":$PORT "; then
        echo -e "${RED}错误: 端口 $PORT 已被占用${NC}"
        echo "请修改 .env 文件中的 MYPRESS_PORT"
        exit 1
    fi
elif command -v netstat &> /dev/null; then
    if netstat -tuln 2>/dev/null | grep -q ":$PORT "; then
        echo -e "${RED}错误: 端口 $PORT 已被占用${NC}"
        echo "请修改 .env 文件中的 MYPRESS_PORT"
        exit 1
    fi
fi

echo -e "${GREEN}  端口 $PORT 可用${NC}"

# 构建 Docker 镜像
echo -e "${YELLOW}[4/6] 构建 Docker 镜像...${NC}"
docker compose build

# 启动服务
echo -e "${YELLOW}[5/6] 启动服务...${NC}"
docker compose up -d

# 等待服务启动并检查健康状态
echo -e "${YELLOW}[6/6] 等待服务就绪...${NC}"
MAX_WAIT=60
WAITED=0
while [ $WAITED -lt $MAX_WAIT ]; do
    if docker compose ps | grep -q "Up\|running"; then
        # 检查 Web 服务是否响应
        HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:$PORT/ 2>/dev/null || echo "000")
        if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ]; then
            break
        fi
    fi
    sleep 3
    WAITED=$((WAITED + 3))
    echo -n "."
done
echo ""

if [ $WAITED -ge $MAX_WAIT ]; then
    echo -e "${YELLOW}服务启动较慢，请稍后手动检查: docker compose logs web${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  MyPress 部署完成!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "前台地址:   ${GREEN}http://localhost:$PORT${NC}"
echo -e "管理后台:   ${GREEN}http://localhost:$PORT/admin/${NC}"
echo ""
echo -e "${YELLOW}下一步：创建超级管理员${NC}"
echo -e "  docker exec -it mypress_web python manage.py createsuperuser"
echo ""
echo "常用命令:"
echo "  查看日志:   docker compose logs -f web"
echo "  重启服务:   docker compose restart web"
echo "  停止服务:   docker compose down"
echo "  数据库备份: ./scripts/backup_db.sh"
echo ""
