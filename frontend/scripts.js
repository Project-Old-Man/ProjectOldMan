const API_BASE_URL = "http://localhost:8000";

document.getElementById("query-button").addEventListener("click", async () => {
    const queryInput = document.getElementById("query-input").value;
    const responseText = document.getElementById("response-text");

    if (!queryInput.trim()) {
        responseText.textContent = "질문을 입력해주세요!";
        return;
    }

    responseText.textContent = "AI가 응답을 생성 중입니다...";

    try {
        const response = await fetch(`${API_BASE_URL}/query`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                question: queryInput,
                user_id: "test_user",
                context: { page: "general" },
            }),
        });

        if (response.ok) {
            const data = await response.json();
            responseText.textContent = data.response;
        } else {
            responseText.textContent = "응답 생성 중 오류가 발생했습니다.";
        }
    } catch (error) {
        responseText.textContent = "서버와의 연결에 실패했습니다.";
        console.error(error);
    }
});

// 추천 결과 가져오기
async function fetchRecommendations() {
    const recommendationList = document.getElementById("recommendation-list");

    try {
        const response = await fetch(`${API_BASE_URL}/recommend`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: "test_user", limit: 5 }),
        });

        if (response.ok) {
            const data = await response.json();
            recommendationList.innerHTML = data.recommendations
                .map((rec) => `<li>${rec.question} (Score: ${rec.score.toFixed(2)})</li>`)
                .join("");
        } else {
            recommendationList.innerHTML = "<li>추천 결과를 가져오는 중 오류가 발생했습니다.</li>";
        }
    } catch (error) {
        recommendationList.innerHTML = "<li>서버와의 연결에 실패했습니다.</li>";
        console.error(error);
    }
}

// 페이지 로드 시 추천 결과 가져오기
fetchRecommendations();
