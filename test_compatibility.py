#!/usr/bin/env python3
"""
프론트엔드와 백엔드 호환성 테스트 스크립트
"""

import requests
import json
import time
import sys
import os
from typing import Dict, Any

# 테스트 설정 - Docker 환경 대응
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

# 필요한 패키지 확인
try:
    import requests
    print("✅ requests 패키지 확인됨")
except ImportError:
    print("❌ requests 패키지가 설치되지 않았습니다.")
    print("설치 명령어: pip install requests")
    sys.exit(1)

def check_prerequisites():
    """사전 요구사항 확인"""
    print("🔍 사전 요구사항 확인 중...")
    
    # Python 버전 확인
    python_version = sys.version_info
    print(f"Python 버전: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 작업 디렉토리 확인
    current_dir = os.getcwd()
    print(f"현재 디렉토리: {current_dir}")
    
    # Docker Compose 파일 존재 확인
    docker_compose_files = ['docker-compose.yml', 'docker-compose.yaml']
    docker_compose_exists = any(os.path.exists(f) for f in docker_compose_files)
    print(f"Docker Compose 파일: {'✅' if docker_compose_exists else '❌'}")
    
    return docker_compose_exists

def check_docker_status():
    """Docker 컨테이너 상태 확인"""
    print("\n🐳 Docker 컨테이너 상태 확인 중...")
    
    import subprocess
    try:
        # Docker가 실행 중인지 확인
        result = subprocess.run(['docker', 'ps'], 
                              capture_output=True, text=True,
                              encoding='utf-8', errors='ignore')
        
        if result.returncode != 0:
            print("❌ Docker가 실행되지 않았습니다.")
            print("Docker Desktop을 시작하고 다시 시도해주세요.")
            return False
        
        # Docker Compose 상태 확인
        result = subprocess.run(['docker-compose', 'ps'], 
                              capture_output=True, text=True,
                              encoding='utf-8', errors='ignore')
        
        if result.returncode == 0:
            print("Docker Compose 상태:")
            print(result.stdout)
            
            # 실행 중인 컨테이너 확인
            running_containers = result.stdout.count('Up')
            if running_containers > 0:
                print(f"✅ {running_containers}개 컨테이너가 실행 중입니다.")
                return True
            else:
                print("❌ 실행 중인 컨테이너가 없습니다.")
                return False
        else:
            print("❌ Docker Compose 상태 확인 실패")
            return False
            
    except FileNotFoundError:
        print("❌ Docker 또는 Docker Compose가 설치되지 않았습니다.")
        return False
    except Exception as e:
        print(f"❌ Docker 상태 확인 중 오류: {e}")
        return False

def test_basic_connection():
    """기본 연결 테스트"""
    print("\n🔍 기본 연결 테스트 중...")
    
    # 백엔드 연결 테스트
    backend_ok = False
    try:
        print(f"백엔드 연결 테스트: {BACKEND_URL}")
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ 백엔드: 연결 성공")
            backend_ok = True
            try:
                data = response.json()
                print(f"   서비스 상태: {data.get('services', {})}")
            except:
                pass
        else:
            print(f"❌ 백엔드: HTTP {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ 백엔드: 연결 거부 (서버가 실행되지 않음)")
    except requests.exceptions.Timeout:
        print("❌ 백엔드: 연결 시간 초과")
    except Exception as e:
        print(f"❌ 백엔드: 연결 오류 - {e}")
    
    # 프론트엔드 연결 테스트
    frontend_ok = False
    try:
        print(f"프론트엔드 연결 테스트: {FRONTEND_URL}")
        response = requests.get(f"{FRONTEND_URL}", timeout=10)
        if response.status_code == 200:
            print("✅ 프론트엔드: 연결 성공")
            frontend_ok = True
        else:
            print(f"❌ 프론트엔드: HTTP {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ 프론트엔드: 연결 거부 (서버가 실행되지 않음)")
    except requests.exceptions.Timeout:
        print("❌ 프론트엔드: 연결 시간 초과")
    except Exception as e:
        print(f"❌ 프론트엔드: 연결 오류 - {e}")
    
    return backend_ok, frontend_ok

def test_simple_query():
    """간단한 API 쿼리 테스트"""
    print("\n🚀 간단한 API 테스트 중...")
    
    test_data = {
        "question": "안녕하세요",
        "user_id": "test_user",
        "context": {"page": "health"}
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/query",
            json=test_data,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API 테스트 성공!")
            print(f"   응답: {data.get('response', '')[:100]}...")
            print(f"   카테고리: {data.get('category', 'N/A')}")
            return True
        else:
            print(f"❌ API 테스트 실패: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"   에러 내용: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   응답 내용: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ API 테스트 실패: {e}")
        return False

def provide_troubleshooting():
    """문제 해결 가이드 제공"""
    print("\n🔧 문제 해결 가이드:")
    print("=" * 50)
    
    print("\n1. Docker 컨테이너가 실행되지 않은 경우:")
    print("   docker-compose up -d --build")
    print("   docker-compose ps")
    
    print("\n2. 백엔드 연결 문제:")
    print("   docker-compose logs backend")
    print("   docker-compose restart backend")
    
    print("\n3. 프론트엔드 연결 문제:")
    print("   docker-compose logs frontend")
    print("   docker-compose restart frontend")
    
    print("\n4. 전체 재시작:")
    print("   docker-compose down")
    print("   docker-compose up -d --build")
    
    print("\n5. 수동 접속 테스트:")
    print("   브라우저에서 http://localhost:3000 접속")
    print("   브라우저에서 http://localhost:8000/docs 접속")

def main():
    """메인 실행 함수"""
    print("🚀 AI 놀이터 연결 테스트 시작")
    print("=" * 50)
    
    # 1. 사전 요구사항 확인
    if not check_prerequisites():
        print("❌ 사전 요구사항을 만족하지 않습니다.")
        return
    
    # 2. Docker 상태 확인
    docker_ok = check_docker_status()
    if not docker_ok:
        print("\n❌ Docker 컨테이너 문제가 있습니다.")
        provide_troubleshooting()
        return
    
    # 3. 기본 연결 테스트
    backend_ok, frontend_ok = test_basic_connection()
    
    if not backend_ok or not frontend_ok:
        print("\n❌ 서비스 연결에 문제가 있습니다.")
        provide_troubleshooting()
        return
    
    # 4. API 기능 테스트
    api_ok = test_simple_query()
    
    if api_ok:
        print("\n🎉 모든 테스트 통과!")
        print("\n🌐 접속 주소:")
        print(f"   - 프론트엔드: {FRONTEND_URL}")
        print(f"   - 백엔드 API: {BACKEND_URL}")
        print(f"   - API 문서: {BACKEND_URL}/docs")
        
        # 추가 테스트 옵션
        try:
            user_input = input("\n더 자세한 테스트를 실행하시겠습니까? (y/N): ").lower()
            if user_input == 'y':
                run_detailed_tests()
        except (EOFError, KeyboardInterrupt):
            print("\n테스트를 종료합니다.")
    else:
        print("\n❌ API 테스트 실패")
        provide_troubleshooting()

def run_detailed_tests():
    """상세 테스트 실행"""
    print("\n🎯 상세 테스트 실행 중...")
    
    # 카테고리별 테스트
    categories = ["health", "travel", "investment", "legal"]
    test_questions = {
        "health": "혈압 관리 방법 알려주세요",
        "travel": "제주도 여행 추천해주세요", 
        "investment": "안전한 투자 방법은?",
        "legal": "계약서 작성시 주의사항"
    }
    
    for category in categories:
        question = test_questions[category]
        print(f"\n📂 {category.upper()} 카테고리 테스트:")
        print(f"   질문: {question}")
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/query",
                json={
                    "question": question,
                    "user_id": f"test_{category}",
                    "context": {"page": category}
                },
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '')
                print(f"   ✅ 응답: {response_text[:80]}...")
                
                # 전문가 역할 확인
                expert_roles = ["전문", "상담", "가이드"]
                has_expert = any(role in response_text for role in expert_roles)
                print(f"   📊 전문가 역할: {'✅' if has_expert else '❌'}")
                
            else:
                print(f"   ❌ 실패: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 오류: {e}")
    
    print("\n✅ 상세 테스트 완료!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n테스트가 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류가 발생했습니다: {e}")
        provide_troubleshooting()