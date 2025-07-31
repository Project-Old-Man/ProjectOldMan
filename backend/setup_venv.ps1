# PowerShell용 Python 가상환경 생성 및 requirements 설치

# 1. venv 생성
python -m venv .venv

# 2. venv 활성화
. .\.venv\Scripts\Activate.ps1

# 3. pip 최신화
python -m pip install --upgrade pip

# 4. requirements.txt 설치
pip install -r requirements.txt

# 5. faiss-cpu, sentence-transformers 등 명시적으로 추가 설치 (필요시)
pip install faiss-cpu sentence-transformers

Write-Host "✅ .venv 가상환경 생성 및 requirements 설치 완료"
Write-Host "가상환경 활성화: .\.venv\Scripts\Activate.ps1"
