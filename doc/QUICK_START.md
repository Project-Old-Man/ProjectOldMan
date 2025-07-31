# 🚀 AI 놀이터 빠른 시작 가이드

## 📋 **필요 조건**

- ✅ Python 3.8 이상
- ✅ Docker (권장)
- ✅ 웹 브라우저
- ✅ 인터넷 연결

---

## 🎯 **방법 1: 프론트엔드만 실행 (가장 간단)**

### 1단계: 터미널 열기
```bash
# Mac에서 Command + Space → "터미널" 검색 → 클릭
```

### 2단계: 프로젝트 폴더로 이동
```bash
cd /Users/Zeu/Downloads/ProjectOldMan/frontend
```

### 3단계: 웹 서버 실행
```bash
python3 -m http.server 8080
```

### 4단계: 브라우저에서 열기
- 브라우저 열기 (Safari, Chrome 등)
- 주소창에 `http://localhost:8080` 입력
- Enter 키 누르기

### ✅ **확인 사항**
- AI 놀이터 메인 페이지가 보임
- 카테고리 메뉴 (건강, 여행, 투자, 법률) 클릭 가능
- 챗봇 버튼 (😊) 클릭 가능
- ⚠️ **챗봇 기능은 백엔드 없이 작동하지 않음**

---

## 🎯 **방법 2: 전체 시스템 실행 (로컬 개발)**

### 1단계: 환경 설정
```bash
cd /Users/Zeu/Downloads/ProjectOldMan
cp env.example .env
```

### 2단계: 여행 문서 임베딩 (최초 1회만 실행)
```bash
cd backend/vector
python embed_travel_docs.py
cd ../..
```

### 3단계: 백엔드 실행 (새 터미널 창)
```bash
cd backend
pip install -r requirements.txt
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4단계: 프론트엔드 실행 (또 다른 터미널 창)
```bash
cd frontend
python3 -m http.server 8080
```

### 5단계: 브라우저에서 확인
- 프론트엔드: `http://localhost:8080`
- 백엔드: `http://localhost:8000`

---

## 🎯 **방법 3: Docker로 전체 실행 (권장)**

### 1단계: Docker 설치 확인
```bash
docker --version
docker-compose --version
```

### 2단계: 환경 설정
```bash
cd /Users/Zeu/Downloads/ProjectOldMan
cp env.example .env
```

### 3단계: 여행 문서 임베딩 (최초 1회만 실행)
```bash
cd backend/vector
python embed_travel_docs.py
cd ../..
```

### 4단계: 전체 시스템 실행
```bash
docker-compose up -d --build
```

### 5단계: 브라우저에서 확인
- 프론트엔드: `http://localhost:3000`
- 백엔드: `http://localhost:8000`

### 6단계: 서비스 상태 확인
```bash
docker-compose ps
```

---

## 🔧 **문제 해결**

### ❌ **포트 충돌 오류**
```bash
# 사용 중인 포트 확인
lsof -i :8000
lsof -i :8080

# 다른 포트로 실행
python3 -m uvicorn main:app --port 8001
python3 -m http.server 8081
```

### ❌ **Python 모듈 없음 오류**
```bash
# 의존성 설치
pip install fastapi uvicorn
```

### ❌ **권한 오류**
```bash
# 포트 80 사용시 (Docker)
sudo docker-compose up -d
```

### ❌ **챗봇 응답 안됨**
- 백엔드가 실행 중인지 확인
- 브라우저 개발자 도구에서 오류 확인
- `http://localhost:8000/health` 접속 테스트

### ❌ **모델 자동 다운로드 실패**
- 인터넷 연결 확인
- Docker의 model_cache 볼륨 확인

### ❌ **임베딩/FAISS 인덱스 없음**
- `embed_travel_docs.py` 재실행

### ❌ **DB 연결 오류**
- `docker-compose logs postgres` 로 로그 확인

### ❌ **CORS 오류**
- 백엔드 CORS 설정 확인

---

## 📱 **모바일에서 접속**

### 같은 Wi-Fi 네트워크에서
1. 컴퓨터 IP 주소 확인
   ```bash
   ifconfig | grep "inet " | grep -v 127.0.0.1
   ```

2. 모바일 브라우저에서 접속
   ```
   http://[컴퓨터IP]:8080
   ```

---

## 🎉 **성공 확인**

### ✅ **정상 작동 시 보이는 것들**
- 🏠 메인 페이지: AI 놀이터 로고와 메뉴
- 💬 챗봇: 우상단 😊 아이콘 클릭
- 📱 반응형: 모바일에서도 잘 보임
- ⚡ 실시간: AI 응답이 빠르게 생성됨

### 🎯 **테스트 질문**
- "안녕하세요"
- "건강에 대해 궁금해요"
- "여행 추천해주세요"

---

## 📞 **도움말**

문제가 발생하면:
1. 터미널 오류 메시지 확인
2. 브라우저 개발자 도구 (F12) 확인
3. `http://localhost:8000/health` 접속 테스트
4. README.md 파일 참조

**즐거운 AI 놀이터 이용하세요! 🎉**