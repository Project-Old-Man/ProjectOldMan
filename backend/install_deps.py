"""
의존성 패키지 설치 스크립트
"""
import subprocess
import sys
import os

def install_package(package, extra_index_url=None):
    """패키지 설치"""
    cmd = [sys.executable, "-m", "pip", "install", package]
    if extra_index_url:
        cmd.extend(["--extra-index-url", extra_index_url])
    
    try:
        print(f"📦 {package} 설치 중...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {package} 설치 완료!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {package} 설치 실패: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False

def main():
    print("🚀 ProjectOldMan 백엔드 의존성 설치 시작...")
    
    # 기본 패키지들
    basic_packages = [
        "fastapi==0.104.1",
        "uvicorn==0.24.0", 
        "pydantic==2.5.0",
        "python-multipart==0.0.6",
        "numpy==1.24.3",
        "sentence-transformers==2.2.2",
        "faiss-cpu==1.7.4",
        "torch==2.1.0",
        "transformers==4.35.0",
        "python-dotenv==1.0.0"
    ]
    
    # 기본 패키지 설치
    for package in basic_packages:
        install_package(package)
    
    # llama-cpp-python 설치 (CPU 최적화)
    print("\n🤖 llama-cpp-python 설치 중 (CPU 최적화)...")
    llama_success = install_package(
        "llama-cpp-python==0.2.20",
        "https://abetlen.github.io/llama-cpp-python/whl/cpu"
    )
    
    if not llama_success:
        print("⚠️ CPU 최적화 버전 설치 실패, 기본 버전 시도...")
        install_package("llama-cpp-python==0.2.20")
    
    print("\n🎉 모든 의존성 설치 완료!")
    print("💡 이제 'python main.py'로 서버를 시작할 수 있습니다.")

if __name__ == "__main__":
    main()
