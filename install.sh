#!/bin/bash

# Màu sắc cho output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}Bắt đầu cài đặt AI Video Production System...${NC}"

# Kiểm tra hệ điều hành
OS=$(uname -s)
if [[ "$OS" != "Linux" && "$OS" != "Darwin" ]]; then
    echo -e "${RED}Hệ điều hành không được hỗ trợ: $OS. Chỉ hỗ trợ Linux và macOS.${NC}"
    exit 1
fi

# Kiểm tra và cài đặt Docker
if ! command -v docker &> /dev/null; then
    echo "Docker chưa được cài đặt. Đang cài đặt Docker..."
    if [[ "$OS" == "Linux" ]]; then
        sudo apt-get update
        sudo apt-get install -y docker.io
        sudo systemctl start docker
        sudo systemctl enable docker
    elif [[ "$OS" == "Darwin" ]]; then
        brew install docker
    fi
else
    echo -e "${GREEN}Docker đã được cài đặt.${NC}"
fi

# Kiểm tra và cài đặt Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose chưa được cài đặt. Đang cài đặt Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    echo -e "${GREEN}Docker Compose đã được cài đặt.${NC}"
fi

# Kiểm tra và cài đặt Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 chưa được cài đặt. Đang cài đặt Python..."
    if [[ "$OS" == "Linux" ]]; then
        sudo apt-get install -y python3 python3-pip
    elif [[ "$OS" == "Darwin" ]]; then
        brew install python3
    fi
else
    echo -e "${GREEN}Python 3 đã được cài đặt.${NC}"
fi

# Cài đặt thư viện Python
echo "Cài đặt các thư viện Python từ requirements.txt..."
pip3 install -r central_controller/requirements.txt

# Kiểm tra file .env
if [ ! -f .env ]; then
    echo "File .env không tồn tại. Tạo từ .env.example..."
    cp .env.example .env
    echo -e "${RED}Vui lòng mở file .env và thêm các API keys cần thiết trước khi tiếp tục!${NC}"
    exit 1
fi

# Khởi động dự án với Docker Compose
echo "Khởi động dự án..."
docker-compose up -d

echo -e "${GREEN}Cài đặt hoàn tất! Truy cập Grafana tại http://localhost:3000 (admin/admin) và Prometheus tại http://localhost:9090.${NC}"
echo "Kiểm tra trạng thái với: docker-compose ps"
echo "Xem logs với: docker-compose logs"