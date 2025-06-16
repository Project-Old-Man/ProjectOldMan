#!/bin/bash
# deploy.sh - 메인 배포 스크립트

set -e

echo "🚀 AI 백엔드 시스템 배포 시작..."

# 환경 변수 설정
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 사전 확인
check_requirements() {
    log_info "시스템 요구사항 확인 중..."
    
    # Docker 확인
    if ! command -v docker &> /dev/null; then
        log_error "Docker가 설치되지 않았습니다"
        exit 1
    fi
    
    # Docker Compose 확인
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose가 설치되지 않았습니다"
        exit 1
    fi
    
    # 메모리 확인 (최소 4GB 권장)
    total_mem=$(free -g | awk '/^Mem:/{print $2}')
    if [ "$total_mem" -lt 4 ]; then
        log_warn "메모리가 4GB 미만입니다. 성능에 영향이 있을 수 있습니다."
    fi
    
    log_info "요구사항 확인 완료"
}

# 환경 설정
setup_environment() {
    log_info "환경 설정 중..."
    
    # 필요한 디렉토리 생성
    mkdir -p logs models data uploads ssl
    
    # .env 파일 확인
    if [ ! -f .env ]; then
        log_warn ".env 파일이 없습니다. 샘플 파일을 복사합니다."
        cp .env.example .env
        log_warn ".env 파일을 수정한 후 다시 실행하세요."
        exit 1
    fi
    
    # 권한 설정
    chmod +x scripts/*.sh
    
    log_info "환경 설정 완료"
}

# 데이터베이스 초기화
init_database() {
    log_info "데이터베이스 초기화 중..."
    
    # PostgreSQL 컨테이너만 먼저 시작
    docker-compose up -d postgres
    
    # 데이터베이스 준비 대기
    log_info "데이터베이스 준비 대기 중..."
    sleep 10
    
    # 데이터베이스 연결 테스트
    max_attempts=30
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose exec -T postgres pg_isready -U postgres; then
            log_info "데이터베이스 연결 성공"
            break
        fi
        
        log_info "데이터베이스 연결 대기 중... ($attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        log_error "데이터베이스 연결 실패"
        exit 1
    fi
}

# 서비스 빌드 및 시작
deploy_services() {
    log_info "서비스 빌드 및 배포 중..."
    
    # 이미지 빌드
    docker-compose build --no-cache
    
    # 모든 서비스 시작
    docker-compose up -d
    
    log_info "서비스 배포 완료"
}

# 헬스체크
health_check() {
    log_info "서비스 상태 확인 중..."
    
    services=("ai-backend:8000/health" "weaviate:8080/v1/meta" "postgres:5432")
    
    for service in "${services[@]}"; do
        IFS=':' read -ra ADDR <<< "$service"
        container=${ADDR[0]}
        endpoint=${ADDR[1]}
        
        log_info "$container 서비스 확인 중..."
        
        max_attempts=30
        attempt=1
        
        while [ $attempt -le $max_attempts ]; do
            if [ "$container" = "postgres" ]; then
                if docker-compose exec -T postgres pg_isready -U postgres &> /dev/null; then
                    log_info "$container 서비스 정상"
                    break
                fi
            else
                if curl -sf "http://localhost:$endpoint" &> /dev/null; then
                    log_info "$container 서비스 정상"
                    break
                fi
            fi
            
            log_info "$container 서비스 대기 중... ($attempt/$max_attempts)"
            sleep 3
            ((attempt++))
        done
        
        if [ $attempt -gt $max_attempts ]; then
            log_error "$container 서비스 시작 실패"
            docker-compose logs $container
            exit 1
        fi
    done
    
    log_info "모든 서비스가 정상적으로 시작되었습니다"
}

# 샘플 데이터 로드
load_sample_data() {
    log_info "샘플 데이터 로드 중..."
    
    # 애플리케이션이 완전히 시작될 때까지 대기
    sleep 30
    
    # 샘플 데이터 로드
    docker-compose exec ai-backend python data_utils.py load_sample
    
    log_info "샘플 데이터 로드 완료"
}

# 메인 배포 프로세스
main() {
    case "${1:-deploy}" in
        "check")
            check_requirements
            ;;
        "setup")
            setup_environment
            ;;
        "db-init")
            init_database
            ;;
        "deploy")
            check_requirements
            setup_environment
            init_database
            deploy_services
            health_check
            load_sample_data
            
            log_info "🎉 배포 완료!"
            log_info "API 문서: http://localhost:8000/docs"
            log_info "Grafana 대시보드: http://localhost:3000 (admin/admin)"
            log_info "Prometheus: http://localhost:9090"
            ;;
        "stop")
            log_info "서비스 중지 중..."
            docker-compose down
            ;;
        "restart")
            log_info "서비스 재시작 중..."
            docker-compose restart
            ;;
        "logs")
            docker-compose logs -f ${2:-ai-backend}
            ;;
        "status")
            docker-compose ps
            ;;
        *)
            echo "사용법: $0 {deploy|check|setup|db-init|stop|restart|logs|status}"
            echo ""
            echo "  deploy  : 전체 시스템 배포"
            echo "  check   : 시스템 요구사항 확인"
            echo "  setup   : 환경 설정"
            echo "  db-init : 데이터베이스 초기화"
            echo "  stop    : 모든 서비스 중지"
            echo "  restart : 모든 서비스 재시작"
            echo "  logs    : 서비스 로그 확인"
            echo "  status  : 서비스 상태 확인"
            exit 1
            ;;
    esac
}

main "$@"

---

#!/bin/bash
# monitoring_setup.sh - 모니터링 대시보드 설정

log_info() {
    echo -e "\033[0;32m[INFO]\033[0m $1"
}

setup_grafana_dashboards() {
    log_info "Grafana 대시보드 설정 중..."
    
    # Grafana가 시작될 때까지 대기
    until curl -sf http://localhost:3000/api/health; do
        echo "Grafana 시작 대기 중..."
        sleep 5
    done
    
    # 기본 데이터소스 추가 (Prometheus)
    curl -X POST \
        -H "Content-Type: application/json" \
        -d '{
            "name": "Prometheus",
            "type": "prometheus",
            "url": "http://prometheus:9090",
            "access": "proxy",
            "isDefault": true
        }' \
        http://admin:admin@localhost:3000/api/datasources
    
    # 기본 대시보드 가져오기
    curl -X POST \
        -H "Content-Type: application/json" \
        -d '{
            "dashboard": {
                "title": "AI Backend Monitoring",
                "panels": [
                    {
                        "title": "API Response Time",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
                            }
                        ]
                    },
                    {
                        "title": "Request Rate",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(http_requests_total[5m])"
                            }
                        ]
                    },
                    {
                        "title": "Error Rate",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(http_requests_total{status=~\"5..\"}[5m])"
                            }
                        ]
                    }
                ]
            },
            "overwrite": true
        }' \
        http://admin:admin@localhost:3000/api/dashboards/db
    
    log_info "Grafana 대시보드 설정 완료"
}

main() {
    setup_grafana_dashboards
}

main "$@"

---

#!/bin/bash
# backup.sh - 백업 스크립트

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

log_info() {
    echo -e "\033[0;32m[INFO]\033[0m $1"
}

backup_database() {
    log_info "데이터베이스 백업 중..."
    
    mkdir -p $BACKUP_DIR/database
    
    docker-compose exec -T postgres pg_dump -U postgres ai_system | \
        gzip > $BACKUP_DIR/database/postgres_backup_$DATE.sql.gz
    
    log_info "데이터베이스 백업 완료: $BACKUP_DIR/database/postgres_backup_$DATE.sql.gz"
}

backup_vector_db() {
    log_info "벡터 데이터베이스 백업 중..."
    
    mkdir -p $BACKUP_DIR/vector_db
    
    docker-compose exec ai-backend python data_utils.py backup \
        --file $BACKUP_DIR/vector_db/weaviate_backup_$DATE.json
    
    log_info "벡터 데이터베이스 백업 완료"
}

backup_logs() {
    log_info "로그 백업 중..."
    
    mkdir -p $BACKUP_DIR/logs
    
    tar -czf $BACKUP_DIR/logs/logs_backup_$DATE.tar.gz logs/
    
    log_info "로그 백업 완료"
}

cleanup_old_backups() {
    log_info "오래된 백업 정리 중..."
    
    # 7일 이상 된 백업 파일 삭제
    find $BACKUP_DIR -name "*backup*" -type f -mtime +7 -delete
    
    log_info "백업 정리 완료"
}

main() {
    case "${1:-all}" in
        "db")
            backup_database
            ;;
        "vector")
            backup_vector_db
            ;;
        "logs")
            backup_logs
            ;;
        "all")
            backup_database
            backup_vector_db
            backup_logs
            cleanup_old_backups
            ;;
        *)
            echo "사용법: $0 {all|db|vector|logs}"
            exit 1
            ;;
    esac
}

main "$@"

---

#!/bin/bash
# performance_test.sh - 성능 테스트 스크립트

log_info() {
    echo -e "\033[0;32m[INFO]\033[0m $1"
}

test_api_endpoint() {
    local endpoint=$1
    local method=${2:-GET}
    local data=${3:-""}
    
    log_info "테스트 중: $method $endpoint"
    
    if [ "$method" = "POST" ] && [ -n "$data" ]; then
        curl -X POST \
            -H "Content-Type: application/json" \
            -d "$data" \
            -w "시간: %{time_total}초, 상태: %{http_code}\n" \
            -s -o /dev/null \
            "http://localhost:8000$endpoint"
    else
        curl -X $method \
            -w "시간: %{time_total}초, 상태: %{http_code}\n" \
            -s -o /dev/null \
            "http://localhost:8000$endpoint"
    fi
}

load_test() {
    local endpoint=$1
    local concurrent=${2:-10}
    local requests=${3:-100}
    
    log_info "부하 테스트 시작: $endpoint (동시접속: $concurrent, 총 요청: $requests)"
    
    # Apache Bench를 사용한 부하 테스트
    if command -v ab &> /dev/null; then
        ab -n $requests -c $concurrent "http://localhost:8000$endpoint"
    else
        log_info "Apache Bench가 설치되지 않아 간단한 테스트로 대체합니다"
        
        for i in $(seq 1 $requests); do
            curl -s -o /dev/null "http://localhost:8000$endpoint" &
            
            # 동시 접속 수 제한
            if (( i % concurrent == 0 )); then
                wait
            fi
        done
        wait
    fi
}

test_query_performance() {
    log_info "쿼리 성능 테스트 중..."
    
    local test_queries=(
        "파이썬이란 무엇인가요?"
        "머신러닝 알고리즘을 설명해주세요"
        "FastAPI 사용법을 알려주세요"
        "데이터베이스 최적화 방법은?"
        "Kubernetes 배포 전략은?"
    )
    
    for query in "${test_queries[@]}"; do
        local data="{\"question\":\"$query\"}"
        test_api_endpoint "/query" "POST" "$data"
        sleep 1
    done
}

main() {
    case "${1:-basic}" in
        "basic")
            log_info "기본 API 테스트 시작"
            test_api_endpoint "/health"
            test_api_endpoint "/analytics/stats"
            test_query_performance
            ;;
        "load")
            log_info "부하 테스트 시작"
            load_test "/health" 20 200
            ;;
        "query")
            test_query_performance
            ;;
        *)
            echo "사용법: $0 {basic|load|query}"
            exit 1
            ;;
    esac
}

main "$@"

---

#!/bin/bash
# update.sh - 시스템 업데이트 스크립트

log_info() {
    echo -e "\033[0;32m[INFO]\033[0m $1"
}

log_warn() {
    echo -e "\033[1;33m[WARN]\033[0m $1"
}

backup_before_update() {
    log_info "업데이트 전 백업 생성 중..."
    ./scripts/backup.sh all
}

update_images() {
    log_info "Docker 이미지 업데이트 중..."
    
    # 최신 이미지 가져오기
    docker-compose pull
    
    # 사용하지 않는 이미지 정리
    docker image prune -f
}

rolling_update() {
    log_info "무중단 업데이트 시작..."
    
    # 서비스별 순차 업데이트
    services=("ai-backend" "nginx")
    
    for service in "${services[@]}"; do
        log_info "$service 업데이트 중..."
        
        # 새 컨테이너 시작
        docker-compose up -d --no-deps --scale $service=2 $service
        
        # 헬스체크 대기
        sleep 30
        
        # 이전 컨테이너 제거
        docker-compose up -d --no-deps --scale $service=1 $service
        
        log_info "$service 업데이트 완료"
    done
}

verify_update() {
    log_info "업데이트 검증 중..."
    
    # 헬스체크
    if curl -sf http://localhost:8000/health; then
        log_info "서비스 정상 동작 확인"
    else
        log_warn "서비스 이상 감지, 롤백을 고려하세요"
        return 1
    fi
    
    # 간단한 기능 테스트
    local test_query='{"question":"테스트 질문입니다"}'
    if curl -sf -X POST \
        -H "Content-Type: application/json" \
        -d "$test_query" \
        http://localhost:8000/query > /dev/null; then
        log_info "기능 테스트 통과"
    else
        log_warn "기능 테스트 실패"
        return 1
    fi
}

rollback() {
    log_info "이전 버전으로 롤백 중..."
    
    # Git에서 이전 커밋으로 되돌리기
    git checkout HEAD~1
    
    # 서비스 재시작
    docker-compose down
    docker-compose up -d
    
    log_info "롤백 완료"
}

main() {
    case "${1:-update}" in
        "update")
            backup_before_update
            update_images
            rolling_update
            
            if verify_update; then
                log_info "업데이트 성공적으로 완료"
            else
                log_warn "업데이트 검증 실패. 롤백을 실행하시겠습니까? (y/N)"
                read -r response
                if [[ "$response" =~ ^[Yy]$ ]]; then
                    rollback
                fi
            fi
            ;;
        "rollback")
            rollback
            ;;
        "verify")
            verify_update
            ;;
        *)
            echo "사용법: $0 {update|rollback|verify}"
            exit 1
            ;;
    esac
}

main "$@"

---

#!/bin/bash
# install_dependencies.sh - 의존성 설치 스크립트

log_info() {
    echo -e "\033[0;32m[INFO]\033[0m $1"
}

log_error() {
    echo -e "\033[0;31m[ERROR]\033[0m $1"
}

detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            echo "debian"
        elif [ -f /etc/redhat-release ]; then
            echo "redhat"
        else
            echo "linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

install_docker_debian() {
    log_info "Docker 설치 중 (Debian/Ubuntu)..."
    
    # 기존 Docker 제거
    sudo apt-get remove -y docker docker-engine docker.io containerd runc
    
    # 저장소 설정
    sudo apt-get update
    sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
    
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Docker 설치
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io
    
    # Docker Compose 설치
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    # 사용자를 docker 그룹에 추가
    sudo usermod -aG docker $USER
    
    log_info "Docker 설치 완료. 다시 로그인한 후 docker 명령어를 사용할 수 있습니다."
}

install_docker_redhat() {
    log_info "Docker 설치 중 (Red Hat/CentOS)..."
    
    # 저장소 추가
    sudo yum install -y yum-utils
    sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    
    # Docker 설치
    sudo yum install -y docker-ce docker-ce-cli containerd.io
    
    # Docker Compose 설치
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    # Docker 서비스 시작
    sudo systemctl start docker
    sudo systemctl enable docker
    
    # 사용자를 docker 그룹에 추가
    sudo usermod -aG docker $USER
    
    log_info "Docker 설치 완료"
}

install_docker_macos() {
    log_info "macOS에서 Docker Desktop을 수동으로 설치해주세요:"
    log_info "https://docs.docker.com/desktop/mac/install/"
    log_error "Docker Desktop 설치 후 다시 실행하세요"
    exit 1
}

install_python_dependencies() {
    log_info "Python 의존성 설치 중..."
    
    # Python 3.11 확인
    if ! command -v python3.11 &> /dev/null; then
        log_info "Python 3.11 설치 중..."
        
        case $(detect_os) in
            "debian")
                sudo apt-get update
                sudo apt-get install -y software-properties-common
                sudo add-apt-repository ppa:deadsnakes/ppa
                sudo apt-get update
                sudo apt-get install -y python3.11 python3.11-pip python3.11-venv
                ;;
            "redhat")
                sudo yum install -y python3.11 python3.11-pip
                ;;
            "macos")
                if command -v brew &> /dev/null; then
                    brew install python@3.11
                else
                    log_error "Homebrew가 설치되지 않았습니다. 수동으로 Python 3.11을 설치하세요."
                    exit 1
                fi
                ;;
        esac
    fi
    
    # 가상환경 생성
    python3.11 -m venv venv
    source venv/bin/activate
    
    # pip 업그레이드
    pip install --upgrade pip
    
    # 의존성 설치
    pip install -r requirements.txt
    
    log_info "Python 의존성 설치 완료"
}

install_monitoring_tools() {
    log_info "모니터링 도구 설치 중..."
    
    case $(detect_os) in
        "debian")
            sudo apt-get install -y apache2-utils curl htop
            ;;
        "redhat")
            sudo yum install -y httpd-tools curl htop
            ;;
        "macos")
            if command -v brew &> /dev/null; then
                brew install apache2 curl htop
            fi
            ;;
    esac
    
    log_info "모니터링 도구 설치 완료"
}

main() {
    log_info "시스템 의존성 설치 시작..."
    
    OS=$(detect_os)
    log_info "감지된 운영체제: $OS"
    
    # Docker 설치
    if ! command -v docker &> /dev/null; then
        case $OS in
            "debian")
                install_docker_debian
                ;;
            "redhat")
                install_docker_redhat
                ;;
            "macos")
                install_docker_macos
                ;;
            *)
                log_error "지원하지 않는 운영체제입니다"
                exit 1
                ;;
        esac
    else
        log_info "Docker가 이미 설치되어 있습니다"
    fi
    
    # Python 의존성 설치
    install_python_dependencies
    
    # 모니터링 도구 설치
    install_monitoring_tools
    
    log_info "모든 의존성 설치 완료!"
    log_info "시스템 배포를 시작하려면 다음 명령어를 실행하세요:"
    log_info "./scripts/deploy.sh deploy"
}

main "$@"
                        