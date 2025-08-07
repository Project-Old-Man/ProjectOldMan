import subprocess
import sys
import os

def run_command(cmd):
    """명령어 실행"""
    print(f"실행: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 성공!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 실패: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    print("🚀 패키지 설치 시작...")
    
    # 1. pip 업그레이드
    print("\n1. pip 업그레이드...")
    run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    # 2. 기본 도구 업그레이드
    print("\n2. 기본 도구 업그레이드...")
    run_command([sys.executable, "-m", "pip", "install", "--upgrade", "setuptools", "wheel"])
    
    # 3. 기본 FastAPI 스택
    print("\n3. FastAPI 스택 설치...")
    basic_packages = [
        "fastapi",
        "uvicorn[standard]",
        "pydantic",
        "python-dotenv"
    ]
    
    for package in basic_packages:
        run_command([sys.executable, "-m", "pip", "install", package])
    
    # 4. NumPy (별도 설치)
    print("\n4. NumPy 설치...")
    run_command([sys.executable, "-m", "pip", "install", "numpy>=1.24.0"])
    
    # 5. llama-cpp-python (CPU 최적화)
    print("\n5. llama-cpp-python 설치...")
    if not run_command([sys.executable, "-m", "pip", "install", "llama-cpp-python", "--no-cache-dir"]):
        print("기본 설치 실패, CPU 최적화 버전 시도...")
        run_command([
            sys.executable, "-m", "pip", "install", "llama-cpp-python",
            "--extra-index-url", "https://abetlen.github.io/llama-cpp-python/whl/cpu"
        ])
    
    # 6. 나머지 패키지
    print("\n6. 나머지 패키지 설치...")
    other_packages = [
        "sentence-transformers",
        "torch",
        "transformers"
    ]
    
    for package in other_packages:
        run_command([sys.executable, "-m", "pip", "install", package])
    
    print("\n🎉 설치 완료! 'python main.py'로 서버를 시작하세요.")

if __name__ == "__main__":
    main()
