let currentCategory = 'health';
let currentTab = 'categories';
let chatHistory = [];

// 백엔드 URL 설정 수정
const BACKEND_URL = window.location.protocol + '//' + window.location.host;

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
    // COMPLETELY FIXED - no dynamic resizing at all
    const fixedTextareaHeight = 80;
    const fixedContainerHeight = 140;
    
    // Force textarea to always be the same height - no calculations needed
    textarea.style.height = fixedTextareaHeight + 'px';
    textarea.style.minHeight = fixedTextareaHeight + 'px';
    textarea.style.maxHeight = fixedTextareaHeight + 'px';
    
    // Get the dynamic input area container
    const inputArea = document.getElementById('dynamicInputArea');
    if (inputArea) {
        // Container is COMPLETELY FIXED - never changes
        inputArea.style.height = `${fixedContainerHeight}px`;
        inputArea.style.minHeight = `${fixedContainerHeight}px`;
        inputArea.style.maxHeight = `${fixedContainerHeight}px`;
        
        // Position is absolutely fixed
        inputArea.style.position = 'fixed';
        inputArea.style.bottom = '0';
        inputArea.style.left = '320px';
        inputArea.style.right = '0';
        inputArea.style.zIndex = '1000';
        inputArea.style.transform = 'none';
        
        // IDENTICAL container styling - never changes
        inputArea.style.background = 'linear-gradient(to right, #f9fafb, #f3f4f6)';
        inputArea.style.borderTop = '2px solid #e5e7eb';
        inputArea.style.padding = '30px 24px';
        inputArea.style.display = 'flex';
        inputArea.style.alignItems = 'center';
        inputArea.style.gap = '16px';
        inputArea.style.boxSizing = 'border-box';
        
        // COMPLETELY FIXED textarea styling - identical every time
        textarea.style.border = '2px solid #e5e7eb';
        textarea.style.borderRadius = '16px';
        textarea.style.background = 'white';
        textarea.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
        textarea.style.padding = '20px 18px';
        textarea.style.fontSize = '16px';
        textarea.style.lineHeight = '1.5';
        textarea.style.outline = 'none';
        textarea.style.resize = 'none';
        textarea.style.width = '100%';
        textarea.style.height = fixedTextareaHeight + 'px';
        textarea.style.minHeight = fixedTextareaHeight + 'px';
        textarea.style.maxHeight = fixedTextareaHeight + 'px';
        textarea.style.overflowY = 'auto';
        textarea.style.boxSizing = 'border-box';
        textarea.style.verticalAlign = 'top'; // Prevent any alignment shifts
        textarea.style.display = 'block'; // Ensure consistent display
        
        // COMPLETELY FIXED send button styling
        const sendButton = document.getElementById('sendButton');
        if (sendButton) {
            sendButton.style.background = 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)';
            sendButton.style.border = 'none';
            sendButton.style.borderRadius = '16px';
            sendButton.style.boxShadow = '0 4px 12px rgba(251, 191, 36, 0.3)';
            sendButton.style.padding = '20px 32px';
            sendButton.style.height = '80px';
            sendButton.style.minHeight = '80px';
            sendButton.style.maxHeight = '80px';
            sendButton.style.minWidth = '100px';
            sendButton.style.flexShrink = '0';
            sendButton.style.display = 'flex';
            sendButton.style.alignItems = 'center';
            sendButton.style.justifyContent = 'center';
            sendButton.style.cursor = 'pointer';
            sendButton.style.fontSize = '18px';
            sendButton.style.fontWeight = '700';
            sendButton.style.color = 'white';
            sendButton.style.boxSizing = 'border-box';
            sendButton.style.verticalAlign = 'top'; // Prevent alignment shifts
        }
        
        // Message container height is also completely fixed
        const messagesContainer = document.getElementById('messagesContainer');
        if (messagesContainer) {
            const chatHeaderHeight = 100;
            const topBannerHeight = 70;
            const totalUsedHeight = topBannerHeight + chatHeaderHeight + fixedContainerHeight;
            const newMessagesHeight = `calc(100vh - ${totalUsedHeight}px)`;
            
            messagesContainer.style.height = newMessagesHeight;
            messagesContainer.style.minHeight = newMessagesHeight;
            messagesContainer.style.maxHeight = newMessagesHeight;
            messagesContainer.style.overflowY = 'auto';
            messagesContainer.style.paddingBottom = '20px';
            
            setTimeout(() => {
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }, 50);
        }
    }
}

// Initialize input area with fixed styling on page load
function initializeInputArea() {
    const inputArea = document.getElementById('dynamicInputArea');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    
    const fixedContainerHeight = 140;
    const fixedTextareaHeight = 80;
    
    if (inputArea) {
        // Set fixed container styling immediately
        inputArea.style.height = `${fixedContainerHeight}px`;
        inputArea.style.minHeight = `${fixedContainerHeight}px`;
        inputArea.style.maxHeight = `${fixedContainerHeight}px`;
        inputArea.style.position = 'fixed';
        inputArea.style.bottom = '0';
        inputArea.style.left = '320px';
        inputArea.style.right = '0';
        inputArea.style.zIndex = '1000';
        inputArea.style.transform = 'none';
        inputArea.style.background = 'linear-gradient(to right, #f9fafb, #f3f4f6)';
        inputArea.style.borderTop = '2px solid #e5e7eb';
        inputArea.style.padding = '30px 24px';
        inputArea.style.display = 'flex';
        inputArea.style.alignItems = 'center';
        inputArea.style.gap = '16px';
        inputArea.style.boxSizing = 'border-box';
    }
    
    if (messageInput) {
        // Set fixed textarea styling immediately
        messageInput.style.height = fixedTextareaHeight + 'px';
        messageInput.style.minHeight = fixedTextareaHeight + 'px';
        messageInput.style.maxHeight = fixedTextareaHeight + 'px';
        messageInput.style.border = '2px solid #e5e7eb';
        messageInput.style.borderRadius = '16px';
        messageInput.style.background = 'white';
        messageInput.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
        messageInput.style.padding = '20px 18px';
        messageInput.style.fontSize = '16px';
        messageInput.style.lineHeight = '1.5';
        messageInput.style.outline = 'none';
        messageInput.style.resize = 'none';
        messageInput.style.width = '100%';
        messageInput.style.overflowY = 'auto';
        messageInput.style.boxSizing = 'border-box';
        messageInput.style.verticalAlign = 'top';
        messageInput.style.display = 'block';
    }
    
    if (sendButton) {
        // Set fixed button styling immediately
        sendButton.style.background = 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)';
        sendButton.style.border = 'none';
        sendButton.style.borderRadius = '16px';
        sendButton.style.boxShadow = '0 4px 12px rgba(251, 191, 36, 0.3)';
        sendButton.style.padding = '20px 32px';
        sendButton.style.height = '80px';
        sendButton.style.minHeight = '80px';
        sendButton.style.maxHeight = '80px';
        sendButton.style.minWidth = '100px';
        sendButton.style.fontSize = '18px';
        sendButton.style.display = 'flex';
        sendButton.style.alignItems = 'center';
        sendButton.style.justifyContent = 'center';
        sendButton.style.flexShrink = '0';
        sendButton.style.cursor = 'pointer';
        sendButton.style.fontWeight = '700';
        sendButton.style.color = 'white';
        sendButton.style.boxSizing = 'border-box';
        sendButton.style.verticalAlign = 'top';
    }
}

// 카테고리 클릭 핸들러 (사이드바용)
function onCategoryClick(category) {
    console.log(`🔄 사이드바에서 카테고리 클릭: ${category}`);
    setCategory(category);
    // 카테고리 탭으로 전환 (필요시)
    if (currentTab !== 'categories') {
        switchTab('categories');
    }
}

// 검색 기능 설정
function setupSearch() {
    const searchBox = document.querySelector('.search-box');
    if (searchBox) {
        searchBox.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            console.log(`🔍 검색어: ${query}`);
            // 검색 기능 구현 (추후 확장)
        });
        
        searchBox.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const query = e.target.value.toLowerCase();
                console.log(`🔍 검색 실행: ${query}`);
                // 검색 실행 로직
            }
        });
    }
}

// 메시지 전송 함수
async function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    
    if (!messageInput) return;
    
    const message = messageInput.value.trim();
    if (!message) return;
    
    // 버튼 비활성화
    if (sendButton) {
        sendButton.disabled = true;
        const buttonText = sendButton.querySelector('span');
        if (buttonText) {
            buttonText.textContent = '전송 중...';
        }
    }
    
    try {
        // 사용자 메시지 추가
        addMessage(message, 'user');
        
        // 입력창 초기화
        messageInput.value = '';
        autoResize(messageInput);
        
        // 타이핑 인디케이터 표시
        showTypingIndicator();
        
        // 백엔드로 메시지 전송 (URL 수정)
        try {
            const apiUrl = `${BACKEND_URL}/api/chat`;
            console.log(`📡 백엔드 호출: ${apiUrl}`);
            console.log(`📝 메시지: ${message}`);
            console.log(`📂 카테고리: ${currentCategory}`);
            
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    category: currentCategory,
                    user_id: `user_${Date.now()}`
                })
            });
            
            console.log(`📡 응답 상태: ${response.status}`);
            
            if (response.ok) {
                const data = await response.json();
                console.log(`✅ 백엔드 응답 성공:`, data);
                
                hideTypingIndicator();
                
                // 응답받은 카테고리로 UI 업데이트
                if (data.category && data.category !== currentCategory) {
                    setCategory(data.category, true);
                }
                
                addMessage(data.response || '죄송합니다. 응답을 받지 못했습니다.', 'bot');
                
                // 채팅 히스토리에 추가
                chatHistory.push({
                    question: message,
                    answer: data.response,
                    category: categoryInfo[data.category]?.title || '일반',
                    time: new Date().toLocaleTimeString()
                });
                
            } else {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }
        } catch (backendError) {
            console.error('❌ 백엔드 연결 실패:', backendError);
            hideTypingIndicator();
            
            let errorMessage = '백엔드 서버에 연결할 수 없습니다.';
            
            if (backendError.message.includes('fetch') || backendError.message.includes('NetworkError')) {
                errorMessage += '\n\n💡 Docker 환경에서 연결 문제가 발생했습니다.\n잠시 후 다시 시도해주세요.';
            }
            
            addMessage(errorMessage, 'bot');
        }
        
    } catch (error) {
        console.error('메시지 전송 오류:', error);
        hideTypingIndicator();
        addMessage('죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요.', 'bot');
    } finally {
        // 버튼 활성화
        if (sendButton) {
            sendButton.disabled = false;
            const buttonText = sendButton.querySelector('span');
            if (buttonText) {
                buttonText.textContent = '전송';
            }
        }
    }
}

// 메시지 추가 함수
function addMessage(text, sender) {
    const container = document.getElementById('messagesContainer');
    if (!container) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message flex ${sender === 'user' ? 'justify-end' : 'justify-start'} mb-4`;
    
    const timestamp = new Date().toLocaleTimeString();
    
    if (sender === 'user') {
        messageDiv.innerHTML = `
            <div class="message-user max-w-xs lg:max-w-md px-4 py-3 rounded-lg bg-amber-500 text-white">
                <div class="message-text menu-font">${text}</div>
                <div class="message-time text-xs text-amber-100 mt-1">${timestamp}</div>
            </div>
        `;
    } else {
        messageDiv.innerHTML = `
            <div class="flex items-start space-x-3 max-w-xs lg:max-w-md">
                <div id="typingIcon" class="nori-icon nori-${currentCategory} flex-shrink-0"></div>
                <div class="message-bot bg-gray-100 px-4 py-3 rounded-lg">
                    <div class="message-text menu-font text-gray-800">${text}</div>
                    <div class="message-time text-xs text-gray-500 mt-1">${timestamp}</div>
                </div>
            </div>
        `;
    }
    
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
    
    // 노리 아이콘 업데이트
    updateNoriIcons(currentCategory);
}

// 타이핑 인디케이터
function showTypingIndicator() {
    const container = document.getElementById('messagesContainer');
    if (!container) return;
    
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typingIndicator';
    typingDiv.className = 'chat-message flex justify-start mb-4';
    typingDiv.innerHTML = `
        <div class="flex items-start space-x-3">
            <div class="nori-icon nori-${currentCategory} flex-shrink-0"></div>
            <div class="bg-gray-100 px-4 py-3 rounded-lg">
                <div class="typing-animation">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        </div>
    `;
    
    container.appendChild(typingDiv);
    container.scrollTop = container.scrollHeight;
    
    // 노리 아이콘 업데이트
    updateNoriIcons(currentCategory);
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// 배너 버튼 핸들러들
function startNewChat() {
    console.log('새 채팅 시작');
    clearChat();
}

function openModels() {
    console.log('AI 모델 열기');
    showModelInfo();
}

function openLab() {
    console.log('실험실 열기');
    addSystemMessage('🧪 실험실 기능은 곧 추가될 예정입니다.');
}

function openChatHistory() {
    console.log('대화 기록 열기');
    switchTab('history');
}

// 사이드바 하단 메뉴 핸들러들
function openSettings() {
    console.log('설정 열기');
    addSystemMessage('⚙️ 설정 기능은 곧 추가될 예정입니다.');
}

function openHelp() {
    console.log('도움말 열기');
    addSystemMessage('❓ 도움말 기능은 곧 추가될 예정입니다.');
}

function openUpgrade() {
    console.log('업그레이드 열기');
    addSystemMessage('⭐ 업그레이드 기능은 곧 추가될 예정입니다.');
}

function openFeedback() {
    console.log('피드백 열기');
    addSystemMessage('💬 피드백 기능은 곧 추가될 예정입니다.');
}

// 배너 버튼 설정 함수 (수정)
function setupBannerButtons() {
    const bannerButtons = document.querySelectorAll('.banner-button');
    bannerButtons.forEach((button, index) => {
        // 폰트 크기를 더 크게 설정
        button.style.fontSize = '18px';
        button.style.fontWeight = '700';
        
        button.addEventListener('click', () => {
            switch(index) {
                case 0: startNewChat(); break;
                case 1: openModels(); break;
                case 2: openLab(); break;
                case 3: openChatHistory(); break;
            }
        });
    });
    
    // 배너 전체 스타일링 확실히 적용
    const bannerContent = document.querySelector('.banner-content');
    if (bannerContent) {
        bannerContent.style.display = 'flex';
        bannerContent.style.justifyContent = 'space-between';
        bannerContent.style.alignItems = 'center';
        bannerContent.style.width = '100%';
        bannerContent.style.padding = '0 32px';
        bannerContent.style.height = '100%';
        bannerContent.style.boxSizing = 'border-box';
    }
    
    // 왼쪽 섹션 스타일링
    const bannerLeft = document.querySelector('.banner-left');
    if (bannerLeft) {
        bannerLeft.style.display = 'flex';
        bannerLeft.style.alignItems = 'center';
        bannerLeft.style.gap = '32px';
        bannerLeft.style.flexShrink = '0';
    }
    
    // 로고 섹션 스타일링
    const logoSection = document.querySelector('.logo-section');
    if (logoSection) {
        logoSection.style.display = 'flex';
        logoSection.style.alignItems = 'center';
        logoSection.style.gap = '16px';
    }
    
    // 버튼 그룹 스타일링
    const buttonGroup = document.querySelector('.button-group');
    if (buttonGroup) {
        buttonGroup.style.display = 'flex';
        buttonGroup.style.alignItems = 'center';
        buttonGroup.style.gap = '12px';
    }
    
    // 오른쪽 섹션 스타일링
    const bannerRight = document.querySelector('.banner-right');
    if (bannerRight) {
        bannerRight.style.display = 'flex';
        bannerRight.style.alignItems = 'center';
        bannerRight.style.gap = '16px';
        bannerRight.style.flexShrink = '0';
    }
    
    // 로고 텍스트 크기 조정
    const logoText = document.querySelector('.logo-font, h1');
    if (logoText) {
        logoText.style.fontSize = '32px';
        logoText.style.fontWeight = '800';
        logoText.style.margin = '0';
    }
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
            initializeInputArea();
            
            // 모델 정보 로드
            loadModelInfo();
            
            // 대화 초기화 및 내보내기 버튼 폰트 크기 조정
            const clearButton = document.querySelector('[onclick="clearChat()"]');
            const exportButton = document.querySelector('[onclick="exportChat()"]');
            
            if (clearButton) {
                clearButton.style.fontSize = '16px'; // 더 큰 폰트
                clearButton.style.fontWeight = '700'; // 더 굵은 폰트
            }
            
            if (exportButton) {
                exportButton.style.fontSize = '16px'; // 더 큰 폰트
                exportButton.style.fontWeight = '700'; // 더 굵은 폰트
            }
            
            // 사이드바의 모든 텍스트 버튼들도 폰트 크기 증가
            const sidebarButtons = document.querySelectorAll('.sidebar button, .sidebar .menu-item');
            sidebarButtons.forEach(button => {
                button.style.fontSize = '15px';
                button.style.fontWeight = '600';
            });
            
            console.log('✅ 이벤트 설정 완료');
        }, 100);
        
    } catch (error) {
        console.error('❌ 컴포넌트 로딩 중 오류:', error);
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
    
    // 백엔드 연결 테스트 (수정)
    try {
        const healthUrl = `${BACKEND_URL}/health`;
        console.log(`🔍 백엔드 헬스체크: ${healthUrl}`);
        
        const response = await fetch(healthUrl);
        if (response.ok) {
            const healthData = await response.json();
            console.log('✅ 백엔드 연결 성공:', healthData);
            addSystemMessage(`🟢 백엔드 서버 연결 성공! 모델: ${healthData.model || 'Unknown'}`);
            
            // 모델 정보 업데이트
            setTimeout(loadModelInfo, 500);
        } else {
            console.log('⚠️ 백엔드 연결 실패:', response.status);
            addSystemMessage('🔄 백엔드 서버가 아직 준비되지 않았습니다. 잠시만 기다려주세요...');
        }
    } catch (error) {
        console.log('⚠️ 백엔드 연결 오류:', error);
        setTimeout(() => {
            addSystemMessage('🔄 백엔드 서버가 시작되고 있습니다. Docker 환경에서는 시간이 걸릴 수 있습니다...');
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

// 모델 정보 조회 및 표시
async function loadModelInfo() {
    try {
        const response = await fetch(`${BACKEND_URL}/api/model-info`);
        if (response.ok) {
            const data = await response.json();
            updateModelStatus(data.model_info);
            console.log('✅ 모델 정보 로드 성공:', data.model_info);
        } else {
            console.log('⚠️ 모델 정보 로드 실패');
            updateModelStatus({ name: 'Unknown', status: 'error' });
        }
    } catch (error) {
        console.error('❌ 모델 정보 로드 오류:', error);
        updateModelStatus({ name: 'Offline', status: 'offline' });
    }
}

// 모델 상태 UI 업데이트
function updateModelStatus(modelInfo) {
    const modelNameElement = document.getElementById('modelName');
    const statusIndicator = document.querySelector('.status-indicator');
    
    if (modelNameElement) {
        modelNameElement.textContent = modelInfo.name || 'Unknown';
    }
    
    if (statusIndicator) {
        // 상태에 따른 색상 변경
        switch (modelInfo.status) {
            case 'loaded':
            case 'active':
                statusIndicator.style.background = '#10b981'; // green
                break;
            case 'mock':
                statusIndicator.style.background = '#f59e0b'; // yellow
                break;
            case 'error':
            case 'file_not_found':
            case 'load_error':
                statusIndicator.style.background = '#ef4444'; // red
                break;
            default:
                statusIndicator.style.background = '#6b7280'; // gray
        }
    }
}

// 모델 정보 상세 표시
async function showModelInfo() {
    try {
        const response = await fetch(`${BACKEND_URL}/api/model-info`);
        if (response.ok) {
            const data = await response.json();
            const modelInfo = data.model_info;
            
            const statusText = {
                'loaded': '로드됨 ✅',
                'active': '활성화됨 ✅', 
                'mock': 'Mock 모드 🟡',
                'file_not_found': '파일 없음 ❌',
                'load_error': '로드 오류 ❌',
                'dependency_missing': '의존성 누락 ❌',
                'offline': '오프라인 ⚫'
            };
            
            const availableModels = modelInfo.available_models || [];
            const availableText = availableModels.length > 0 
                ? `\n\n🗂️ 사용 가능한 모델:\n${availableModels.map(m => `• ${m.name} (${(m.size_mb || 0).toFixed(1)}MB)`).join('\n')}`
                : '\n\n📁 models/ 디렉토리에 모델 파일이 없습니다.';
            
            addSystemMessage(`🤖 현재 AI 모델 정보:
📋 이름: ${modelInfo.name}
📊 상태: ${statusText[modelInfo.status] || modelInfo.status}
📂 경로: ${modelInfo.path}
🔧 타입: ${modelInfo.type}
🎯 임베딩: ${modelInfo.embedding_status?.status || 'Unknown'}${availableText}`);
            
        } else {
            addSystemMessage('❌ 모델 정보를 가져올 수 없습니다.');
        }
    } catch (error) {
        console.error('모델 정보 조회 오류:', error);
        addSystemMessage('❌ 모델 정보 조회 중 오류가 발생했습니다.');
    }
}