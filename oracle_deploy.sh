#!/bin/bash

# Oracle Cloud Free Tier 배포 스크립트
echo "🚀 Oracle Cloud Free Tier 배포 시작..."

# 시스템 업데이트
echo "📦 시스템 업데이트 중..."
sudo apt update && sudo apt upgrade -y

# Docker 설치
echo "🐳 Docker 설치 중..."
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Docker Compose 설치
echo "📋 Docker Compose 설치 중..."
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 현재 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER

# 메모리 최적화 설정
echo "⚙️ 메모리 최적화 설정 중..."
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
echo 'vm.vfs_cache_pressure=50' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# 스왑 파일 생성 (필요시)
if [ ! -f /swapfile ]; then
    echo "💾 스왑 파일 생성 중..."
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi

# 프로젝트 디렉토리 생성
echo "📁 프로젝트 디렉토리 설정 중..."
mkdir -p ~/projectoldman
cd ~/projectoldman

# 환경 변수 설정
echo "🔧 환경 변수 설정 중..."
cat > .env << EOF
# Oracle Cloud Free Tier 최적화 설정
DATABASE_URL=postgresql://username:password@postgres:5432/database_name
WEAVIATE_URL=http://weaviate:8080
LLM_MODEL=microsoft/DialoGPT-medium
MAX_TOKENS=512
TEMPERATURE=0.7
TOP_P=0.9
TENSOR_PARALLEL_SIZE=1
GPU_MEMORY_UTILIZATION=0.0
MAX_MODEL_LEN=2048
MAX_NUM_BATCHED_TOKENS=4096
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
EOF

# Docker 서비스 시작
echo "🔧 Docker 서비스 시작 중..."
sudo systemctl start docker
sudo systemctl enable docker

# 메모리 상태 확인
echo "📊 메모리 상태 확인:"
free -h

echo "✅ Oracle Cloud Free Tier 배포 준비 완료!"
echo "📝 다음 단계:"
echo "1. 프로젝트 파일을 이 서버에 업로드"
echo "2. docker-compose up --build 실행"
echo "3. 모델 다운로드 완료까지 대기 (처음 실행 시 시간 소요)" 