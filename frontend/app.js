let currentCategory = 'health';
let currentTab = 'categories';
let chatHistory = [];

const BACKEND_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000' 
    : 'http://localhost:8000';

const categoryInfo = {
    health: { 
        title: '건강 상담', 
        subtitle: '건강에 관한 궁금한 점을 물어보세요',
        prompt: '건강 전문 AI가 도움을 드릴게요!'
    },
    travel: { 
        title: '여행 상담', 
        subtitle: '여행 계획과 정보를 도움을 드려요',
        prompt: '여행 전문 AI가 맞춤 정보를 제공할게요!'
    },
    investment: { 
        title: '투자 상담', 
        subtitle: '투자와 재테크 정보를 제공해요',
        prompt: '투자 전문 AI가 안전한 정보를 알려드릴게요!'
    },
    legal: { 
        title: '법률 상담', 
        subtitle: '법률 관련 궁금증을 해결해드려요',
        prompt: '법률 전문 AI가 기본 정보를 제공할게요!'
    }
};

// Component loading function
async function loadComponent(elementId, componentPath) {
    try {
        const response = await fetch(componentPath);
        const html = await response.text();
        document.getElementById(elementId).innerHTML = html;
        console.log(`✅ 컴포넌트 로드 완료: ${componentPath}`);
    } catch (error) {
        console.error(`❌ 컴포넌트 로드 실패 ${componentPath}:`, error);
        // 폴백으로 기본 HTML 구조 제공
        if (elementId === 'header-container') {
            document.getElementById(elementId).innerHTML = '<div>헤더 로딩 중...</div>';
        } else if (elementId === 'sidebar-container') {
            document.getElementById(elementId).innerHTML = '<div>사이드바 로딩 중...</div>';
        } else if (elementId === 'chat-container') {
            document.getElementById(elementId).innerHTML = '<div>채팅 영역 로딩 중...</div>';
        }
    }
}

// 탭 전환 함수
function switchTab(tabName) {
    console.log(`탭 전환: ${tabName}`);
    currentTab = tabName;
    
    // 탭 버튼 스타일 업데이트
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById(tabName + 'Tab').classList.add('active');
    
    // 탭 컨텐츠 표시/숨김
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.add('hidden');
    });
    document.getElementById(tabName + 'Content').classList.remove('hidden');
    
    if (tabName === 'history') loadChatHistory();
    else if (tabName === 'recommendations') {
        setTimeout(() => {
            highlightRecommendationCategory(currentCategory);
        }, 100);
    }
}

// 카테고리 변경 함수
function setCategory(category, skipWelcomeMessage = false) {
    console.log(`🔄 카테고리 변경: ${currentCategory} → ${category}`);
    currentCategory = category;
    
    // 카테고리 버튼 스타일 업데이트
    document.querySelectorAll('.category-button').forEach(btn => {
        btn.classList.remove('active');
    });
    const categoryButton = document.querySelector(`[data-category="${category}"]`);
    if (categoryButton) {
        categoryButton.classList.add('active');
        console.log(`✅ 카테고리 버튼 활성화: ${category}`);
    }
    
    // 헤더 업데이트
    const titleElement = document.getElementById('chatTitle');
    const subtitleElement = document.getElementById('chatSubtitle');
    if (titleElement && subtitleElement) {
        titleElement.textContent = categoryInfo[category].title;
        subtitleElement.textContent = categoryInfo[category].subtitle;
        console.log(`✅ 헤더 업데이트 완료: ${categoryInfo[category].title}`);
    }
    
    // 노리 아이콘 업데이트
    updateNoriIcons(category);
    
    // 추천 탭에서 해당 카테고리 하이라이트
    highlightRecommendationCategory(category);
    
    // 환영 메시지 표시
    if (!skipWelcomeMessage && currentTab === 'categories') {
        setTimeout(() => {
            const welcomeMessage = `안녕하세요! ${categoryInfo[category].prompt}`;
            addMessage(welcomeMessage, 'bot');
        }, 500);
    }
}

// 노리 아이콘 업데이트 함수
function updateNoriIcons(category) {
    console.log(`🎨 노리 아이콘 업데이트: ${category}`);
    const timestamp = Date.now();
    const noriClass = `nori-${category}`;
    const imageUrl = `./images/nori-${category}.png?v=${timestamp}`;
    
    // 헤더 아이콘
    const chatHeaderIcon = document.getElementById('chatHeaderIcon');
    if (chatHeaderIcon) {
        chatHeaderIcon.className = `nori-icon nori-large ${noriClass}`;
        chatHeaderIcon.style.backgroundImage = `url('${imageUrl}')`;
    }
    
    // 환영 메시지 아이콘
    const welcomeIcon = document.getElementById('welcomeIcon');
    if (welcomeIcon) {
        welcomeIcon.className = `nori-icon nori-xl ${noriClass} mx-auto mb-3`;
        welcomeIcon.style.backgroundImage = `url('${imageUrl}')`;
    }
    
    // 타이핑 인디케이터 아이콘
    const typingIcon = document.getElementById('typingIcon');
    if (typingIcon) {
        typingIcon.className = `nori-icon ${noriClass}`;
        typingIcon.style.backgroundImage = `url('${imageUrl}')`;
    }
}

// 추천 질문 클릭 함수
async function askRecommendedQuestion(targetCategory, question) {
    console.log(`🎯 추천 질문 클릭됨!`);
    console.log(`  📂 대상 카테고리: ${targetCategory}`);
    console.log(`  💬 질문: ${question}`);
    
    try {
        // 카테고리 변경 (필요한 경우)
        if (currentCategory !== targetCategory) {
            console.log('1️⃣ 카테고리 변경 중...');
            setCategory(targetCategory, true);
            await new Promise(resolve => setTimeout(resolve, 300));
        }
        
        // 시스템 메시지로 사용자에게 알림
        console.log('2️⃣ 시스템 메시지 표시...');
        addSystemMessage(`🔄 ${categoryInfo[targetCategory].title} 카테고리로 전환했습니다.`);
        
        // 입력창에 질문 자동 설정
        const messageInput = document.getElementById('messageInput');
        if (messageInput) {
            messageInput.value = question;
            autoResize(messageInput);
        }
        
        // 잠시 대기 후 자동 전송
        await new Promise(resolve => setTimeout(resolve, 800));
        await sendMessage();
        
        // 추천 탭에서 카테고리 하이라이트 업데이트
        highlightRecommendationCategory(targetCategory);
        
        console.log('🎉 추천 질문 처리 완료!');
        
    } catch (error) {
        console.error('❌ 추천 질문 처리 중 오류:', error);
        addSystemMessage(`❌ 오류가 발생했습니다: ${error.message}`);
    }
}

// 시스템 메시지 추가 함수
function addSystemMessage(text) {
    console.log(`📢 시스템 메시지: ${text}`);
    const container = document.getElementById('messagesContainer');
    if (!container) return;
    
    // 기존에 같은 메시지가 있는지 확인
    const existingMessages = container.querySelectorAll('.system-message');
    const isDuplicate = Array.from(existingMessages).some(msg => 
        msg.textContent.includes(text.replace(/🔄|💡|❌/g, '').trim())
    );
    
    if (isDuplicate) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'text-center my-3 chat-message system-message';
    messageDiv.innerHTML = `
        <div class="inline-block bg-blue-50 border border-blue-200 rounded-lg px-3 py-2 text-sm text-blue-800 menu-font animate-pulse">
            ${text}
        </div>
    `;
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
    
    // 3초 후 메시지 제거
    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.style.opacity = '0';
            setTimeout(() => {
                if (messageDiv.parentNode) {
                    messageDiv.parentNode.removeChild(messageDiv);
                }
            }, 500);
        }
    }, 3000);
}

// 추천 질문 셔플 함수
function shuffleRecommendations() {
    console.log('🔄 추천 질문 셔플...');
    
    const allRecommendations = {
        health: [
            { q: "혈압 관리 방법 알려주세요", desc: "중장년층 건강 관리" },
            { q: "당뇨 예방은 어떻게 하나요?", desc: "성인병 예방법" },
            { q: "건강한 운동법이 궁금해요", desc: "중장년층 맞춤 운동" },
            { q: "건강검진 주기는 어떻게 되나요?", desc: "정기 건강검진" },
            { q: "콜레스테롤 관리법 알려주세요", desc: "혈관 건강" },
            { q: "골다공증 예방 방법은?", desc: "뼈 건강" },
            { q: "스트레스 관리 방법", desc: "정신 건강" },
            { q: "수면의 질 개선 방법", desc: "수면 건강" }
        ],
        travel: [
            { q: "제주도 여행 추천해주세요", desc: "인기 여행지" },
            { q: "부산 여행 코스 알려주세요", desc: "바다 여행" },
            { q: "경주 역사 여행 계획 세워주세요", desc: "문화재 탐방" },
            { q: "여행 준비물은 뭐가 필요한가요?", desc: "여행 팁" },
            { q: "강릉 여행 코스 추천해주세요", desc: "동해안 여행" },
            { q: "전주 한옥마을 여행 계획", desc: "전통 문화" },
            { q: "여행자 보험 가입 방법", desc: "여행 준비" },
            { q: "온천 여행지 추천해주세요", desc: "힐링 여행" }
        ],
        investment: [
            { q: "안전한 투자 방법은?", desc: "저위험 투자" },
            { q: "연금 준비 어떻게 하나요?", desc: "은퇴 계획" },
            { q: "부동산 투자 주의사항은?", desc: "부동산 투자" },
            { q: "적금과 예금 어떤게 좋을까요?", desc: "기본 금융상품" },
            { q: "국채 투자 방법 알려주세요", desc: "안전 투자" },
            { q: "펀드 투자 기초 지식", desc: "간접 투자" },
            { q: "ISA 계좌란 무엇인가요?", desc: "세제혜택 상품" },
            { q: "퇴직연금 관리 방법", desc: "퇴직 준비" }
        ],
        legal: [
            { q: "계약서 작성시 주의사항", desc: "계약 법률" },
            { q: "상속 준비 방법", desc: "상속 법률" },
            { q: "사기 예방법 알려주세요", desc: "소비자 보호" },
            { q: "유언장 작성 방법", desc: "상속 준비" },
            { q: "임대차 계약 주의사항", desc: "부동산 법률" },
            { q: "소비자 분쟁 해결 방법", desc: "소비자 권익" },
            { q: "의료사고 대처 방법", desc: "의료 법률" },
            { q: "노인장기요양보험 신청법", desc: "복지 혜택" }
        ]
    };

    // 각 카테고리별로 추천 질문 업데이트
    Object.keys(allRecommendations).forEach(category => {
        const recommendations = allRecommendations[category];
        const shuffled = recommendations.sort(() => 0.5 - Math.random()).slice(0, 4);
        const cards = document.querySelectorAll(`.${category}-rec`);
        
        shuffled.forEach((rec, index) => {
            if (cards[index]) {
                const card = cards[index];
                
                // 새로운 클릭 이벤트 핸들러 생성
                const clickHandler = (event) => {
                    event.preventDefault();
                    event.stopPropagation();
                    askRecommendedQuestion(category, rec.q);
                };
                
                // 기존 이벤트 제거
                card.onclick = null;
                card.removeEventListener('click', card._clickHandler);
                
                // 이벤트 핸들러 저장 및 등록
                card._clickHandler = clickHandler;
                card.onclick = clickHandler;
                card.addEventListener('click', clickHandler);
                card.style.cursor = 'pointer';
                
                // 텍스트 업데이트
                const titleElement = card.querySelector('.card-title');
                const metaElement = card.querySelector('.card-meta');
                
                if (titleElement) titleElement.textContent = rec.q;
                if (metaElement) metaElement.textContent = rec.desc;
            }
        });
    });

    addSystemMessage("🔄 새로운 추천 질문이 준비되었습니다!");
}

// 추천 탭에서 선택된 카테고리 하이라이트
function highlightRecommendationCategory(category) {
    console.log(`🎨 추천 카테고리 하이라이트: ${category}`);
    
    // 모든 추천 카테고리 초기화
    document.querySelectorAll('.recommendation-category').forEach(cat => {
        cat.style.backgroundColor = '';
        cat.style.border = '';
        cat.style.borderRadius = '';
        cat.style.padding = '';
        cat.style.transform = '';
        cat.style.boxShadow = '';
    });
    
    // 선택된 카테고리 하이라이트
    const categoryMap = {
        'health': 0,
        'travel': 1, 
        'investment': 2,
        'legal': 3
    };
    
    const categoryIndex = categoryMap[category];
    if (categoryIndex !== undefined) {
        const categoryElements = document.querySelectorAll('.recommendation-category');
        const categoryElement = categoryElements[categoryIndex];
        if (categoryElement) {
            categoryElement.style.backgroundColor = '#fef3c7';
            categoryElement.style.border = '2px solid #fbbf24';
            categoryElement.style.borderRadius = '12px';
            categoryElement.style.padding = '12px';
            categoryElement.style.transform = 'scale(1.02)';
            categoryElement.style.boxShadow = '0 8px 25px rgba(251, 191, 36, 0.3)';
        }
    }
}

// 대화 초기화
function clearChat() {
    if (confirm('대화를 모두 삭제하시겠습니까?')) {
        document.getElementById('messagesContainer').innerHTML = `
            <div class="flex justify-center mb-8">
                <div class="welcome-card">
                    <div id="welcomeIcon" class="nori-icon nori-xl nori-${currentCategory} mx-auto mb-4"></div>
                    <h3 class="welcome-title logo-font">새로운 대화를 시작하세요!</h3>
                    <p class="welcome-subtitle menu-font">궁금한 것이 있으시면 언제든 물어보세요. 노리가 도와드릴게요!</p>
                </div>
            </div>
        `;
        chatHistory = [];
    }
}

function exportChat() {
    const messages = document.querySelectorAll('.chat-message');
    let exportText = `AI 놀이터 대화 내역\n날짜: ${new Date().toLocaleDateString()}\n카테고리: ${categoryInfo[currentCategory].title}\n\n`;
    
    messages.forEach(msg => {
        const text = msg.textContent.trim();
        const isUser = msg.querySelector('.message-user');
        const sender = isUser ? '사용자' : 'AI';
        exportText += `${sender}: ${text}\n\n`;
    });
    
    const blob = new Blob([exportText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `AI놀이터_대화내역_${new Date().toISOString().split('T')[0]}.txt`;
    a.click();
    URL.revokeObjectURL(url);
}

function loadChatHistory() {
    const historyContainer = document.getElementById('chatHistory');
    historyContainer.innerHTML = '';
    
    if (chatHistory.length === 0) {
        historyContainer.innerHTML = '<p class="text-gray-500 text-center py-6 text-base menu-font">아직 대화 기록이 없습니다.</p>';
        return;
    }
    
    chatHistory.slice(-10).reverse().forEach(item => {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-card';
        
        let noriClass = 'nori-icon';
        if (item.category.includes('건강')) noriClass += ' nori-health';
        else if (item.category.includes('여행')) noriClass += ' nori-travel';
        else if (item.category.includes('투자')) noriClass += ' nori-investment';
        else if (item.category.includes('법률')) noriClass += ' nori-legal';
        
        historyItem.innerHTML = `
            <div class="flex items-start space-x-2">
                <div class="${noriClass} flex-shrink-0"></div>
                <div class="card-content">
                    <div class="card-title menu-font font-medium">${item.question}</div>
                    <div class="card-meta menu-font">${item.category} • ${item.time}</div>
                </div>
            </div>
        `;
        historyItem.onclick = () => {
            document.getElementById('messageInput').value = item.question;
            switchTab('categories');
        };
        historyContainer.appendChild(historyItem);
    });
}

function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}

function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    addMessage(message, 'user');
    input.value = '';
    input.style.height = 'auto';
    
    chatHistory.push({
        question: message,
        category: categoryInfo[currentCategory].title,
        time: new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
    });
    
    showTypingIndicator();
    
    try {
        const response = await fetch(`${BACKEND_URL}/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question: message,
                user_id: 'user_' + Date.now(),
                context: { 
                    page: currentCategory,
                    timestamp: new Date().toISOString(),
                    category_info: categoryInfo[currentCategory]
                }
            })
        });

        hideTypingIndicator();

        if (response.ok) {
            const data = await response.json();
            addMessage(data.response, 'bot');
            
            if (data.category && categoryInfo[data.category]) {
                setTimeout(() => {
                    addHelpMessage(data.category);
                }, 1000);
            }
        } else {
            addMessage('죄송합니다. 서버 연결에 문제가 있습니다.', 'bot');
        }
    } catch (error) {
        hideTypingIndicator();
        addMessage('네트워크 오류가 발생했습니다. 잠시 후 다시 시도해주세요.', 'bot');
    }
}

function addHelpMessage(category) {
    const helpMessages = {
        health: "더 구체적인 건강 상담을 원하시면 '혈압', '당뇨', '운동', '식단' 등의 키워드로 질문해보세요!",
        travel: "여행지, 일정, 준비물 등에 대해 더 자세히 문의하실 수 있어요!",
        investment: "안전한 투자, 연금, 재테크 등에 대해 더 질문해보세요!",
        legal: "계약, 상속, 법률상담 등에 대해 더 문의하실 수 있어요!"
    };
    
    if (helpMessages[category]) {
        const helpDiv = document.createElement('div');
        helpDiv.className = 'text-center my-4';
        helpDiv.innerHTML = `
            <div class="inline-block bg-yellow-50 border border-yellow-200 rounded-lg px-4 py-2 text-sm text-yellow-800">
                💡 ${helpMessages[category]}
            </div>
        `;
        document.getElementById('messagesContainer').appendChild(helpDiv);
        document.getElementById('messagesContainer').scrollTop = document.getElementById('messagesContainer').scrollHeight;
    }
}

function addMessage(text, sender) {
    const container = document.getElementById('messagesContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message mb-5 flex`;
    
    const noriClass = `nori-${currentCategory}`;
    
    const messageContent = `
        <div class="${sender === 'user' ? 'message-user' : 'message-bot'}">
            ${sender === 'bot' ? `<div class="flex items-start space-x-3"><div class="nori-icon ${noriClass} mt-1"></div><div>` : '' }
            <p class="leading-relaxed message-font">${text}</p>
            ${sender === 'bot' ? '</div></div>' : '' }
        </div>
    `;
    
    messageDiv.innerHTML = messageContent;
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}

function showTypingIndicator() {
    document.getElementById('typingIndicator').classList.remove('hidden');
    document.getElementById('messagesContainer').scrollTop = document.getElementById('messagesContainer').scrollHeight;
}

function hideTypingIndicator() {
    document.getElementById('typingIndicator').classList.add('hidden');
}

// 카테고리 버튼 클릭 시 호출되는 함수
function onCategoryClick(category) {
    console.log(`🖱️ 카테고리 버튼 클릭: ${category}`);
    setCategory(category, false);
}

// 새로운 기능 함수들
function openSettings() {
    console.log('설정 페이지 열기');
    addSystemMessage('⚙️ 설정 기능은 곧 업데이트됩니다!');
}

function openHelp() {
    console.log('도움말 페이지 열기');
    addSystemMessage(`
        📚 AI 놀이터 사용법:
        
        • 카테고리별 전문 상담: 건강, 여행, 투자, 법률
        • 추천 질문: 각 분야별 맞춤 질문 제공
        • 대화 히스토리: 이전 대화 내용 확인
        • 내보내기: 대화 내용을 파일로 저장
        
        더 궁금한 점이 있으시면 언제든 질문해주세요!
    `);
}

function openUpgrade() {
    console.log('업그레이드 페이지 열기');
    addSystemMessage('⭐ AI 놀이터 프리미엄 기능은 준비 중입니다!');
}

function openFeedback() {
    console.log('피드백 페이지 열기');
    addSystemMessage('💬 피드백을 남겨주세요! 여러분의 의견이 AI 놀이터를 더욱 발전시킵니다.');
}

function startNewChat() {
    clearChat();
    addSystemMessage('🆕 새로운 대화를 시작했습니다!');
}

function openModels() {
    addSystemMessage('🤖 AI 모델 선택 기능은 곧 추가됩니다!');
}

function openLab() {
    addSystemMessage('🧪 실험실 기능은 개발 중입니다!');
}

function openChatHistory() {
    switchTab('history');
    addSystemMessage('📋 대화 기록을 확인하세요!');
}

function setupSearch() {
    const searchBox = document.querySelector('.search-box');
    if (searchBox) {
        searchBox.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const searchTerm = this.value.trim();
                if (searchTerm) {
                    addSystemMessage(`🔍 "${searchTerm}" 검색 기능은 곧 추가됩니다!`);
                    this.value = '';
                }
            }
        });
    }
}

function setupBannerButtons() {
    const bannerButtons = document.querySelectorAll('.banner-button');
    bannerButtons.forEach((button, index) => {
        button.addEventListener('click', () => {
            switch(index) {
                case 0: startNewChat(); break;
                case 1: openModels(); break;
                case 2: openLab(); break;
                case 3: openChatHistory(); break;
            }
        });
    });
}

// 페이지 로드시 초기화
window.onload = async function() {
    console.log('🚀 페이지 로딩 시작...');
    
    try {
        // Load components
        await loadComponent('header-container', './components/header.html');
        await loadComponent('sidebar-container', './components/sidebar.html');
        await loadComponent('chat-container', './components/chat.html');
        
        // 컴포넌트 로딩 후 이벤트 설정
        setTimeout(() => {
            setupSearch();
            setupBannerButtons();
            console.log('✅ 이벤트 설정 완료');
        }, 100);
        
    } catch (error) {
        console.error('❌ 컴포넌트 로딩 중 오류:', error);
        // 컴포넌트 로딩 실패시 기본 구조로 폴백
        createFallbackStructure();
    }
    
    // 노리 이미지 캐시 버스팅
    const timestamp = Date.now();
    const categoryMapping = {
        'nori-health': 'nori-health.png',
        'nori-travel': 'nori-travel.png',
        'nori-investment': 'nori-investment.png',
        'nori-legal': 'nori-legal.png'
    };
    
    setTimeout(() => {
        Object.keys(categoryMapping).forEach(className => {
            const elements = document.querySelectorAll(`.${className}`);
            elements.forEach(el => {
                el.style.backgroundImage = `url('./images/${categoryMapping[className]}?v=${timestamp}')`;
            });
        });
    }, 200);
    
    // 백엔드 연결 테스트
    try {
        const response = await fetch(`${BACKEND_URL}/health`);
        if (response.ok) {
            console.log('✅ 백엔드 연결 성공');
        } else {
            console.log('⚠️ 백엔드 연결 실패');
        }
    } catch (error) {
        console.log('⚠️ 백엔드 연결 오류:', error);
        setTimeout(() => {
            addSystemMessage('🔄 백엔드 서버가 시작되고 있습니다. 잠시만 기다려주세요...');
        }, 1000);
    }
    
    // 추천 질문 초기화
    setTimeout(() => {
        console.log('🎯 추천 질문 시스템 초기화...');
        try {
            shuffleRecommendations();
            highlightRecommendationCategory(currentCategory);
            console.log('✅ 추천 질문 시스템 초기화 완료');
        } catch (error) {
            console.error('❌ 추천 질문 초기화 실패:', error);
        }
    }, 2500);
    
    console.log('✅ 페이지 로딩 완료');
};

// 폴백 구조 생성 함수
function createFallbackStructure() {
    console.log('🔄 폴백 구조 생성 중...');
    
    // 헤더 폴백
    document.getElementById('header-container').innerHTML = `
        <header class="top-banner">
            <div class="banner-content">
                <h1 class="text-2xl font-bold text-amber-900 logo-font">AI 놀이터</h1>
                <div>로딩 중...</div>
            </div>
        </header>
    `;
    
    // 사이드바 폴백  
    document.getElementById('sidebar-container').innerHTML = `
        <aside class="sidebar bg-gradient-to-b from-gray-50 to-gray-100 border-r-2 border-gray-200">
            <div class="p-6">
                <div class="text-center">컴포넌트 로딩 중...</div>
            </div>
        </aside>
    `;
    
    // 채팅 영역 폴백
    document.getElementById('chat-container').innerHTML = `
        <main class="chat-container">
            <div class="p-6">
                <div class="text-center">채팅 영역 로딩 중...</div>
            </div>
        </main>
    `;
}