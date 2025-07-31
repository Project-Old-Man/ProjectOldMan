from typing import List, Dict, Any, Optional
import json
import os
import logging

logger = logging.getLogger(__name__)

class PromptManager:
    def __init__(self):
        self.templates = self._load_templates()
        self.system_prompt = self._load_system_prompt()
    
    def _load_templates(self) -> Dict[str, str]:
        """프롬프트 템플릿 로드"""
        return {
            "query_basic": """당신은 도움이 되는 AI 어시스턴트입니다. 주어진 컨텍스트를 바탕으로 사용자의 질문에 정확하고 유용한 답변을 제공하세요.

컨텍스트:
{context}

질문: {question}

답변:""",
            
            "query_with_source": """당신은 전문적인 AI 어시스턴트입니다. 제공된 자료를 바탕으로 사용자의 질문에 답변하되, 답변 끝에 참고한 출처를 명시하세요.

참고 자료:
{context}

사용자 질문: {question}

답변 (출처 포함):""",
            
            "recommendation": """사용자의 이전 관심사와 질문 패턴을 분석하여 맞춤형 추천을 제공하세요.

사용자 히스토리:
{user_history}

관련 컨텐츠:
{related_content}

추천 이유와 함께 3-5개의 관련 주제나 질문을 추천해주세요:""",
            
            "feedback_analysis": """다음 사용자 피드백을 분석하여 시스템 개선점을 제안하세요.

질문: {question}
답변: {response}
사용자 평가: {rating}/5
피드백 내용: {feedback_text}

분석 결과와 개선 방안:""",
            
            "context_summarization": """다음 문서들의 핵심 내용을 요약하여 질문 답변에 활용할 수 있도록 정리하세요.

문서 내용:
{documents}

핵심 요약:"""
        }
    
    def _load_system_prompt(self) -> str:
        """시스템 프롬프트 로드"""
        return """당신은 한국어를 능숙하게 구사하는 전문 AI 어시스턴트입니다.

주요 역할:
1. 사용자의 질문을 정확히 이해하고 도움이 되는 답변 제공
2. 제공된 컨텍스트 정보를 바탕으로 사실적이고 근거 있는 답변
3. 불확실한 정보에 대해서는 솔직하게 모른다고 표현
4. 항상 예의 바르고 친근한 톤으로 소통

답변 가이드라인:
- 간결하면서도 충분한 정보 제공
- 구체적인 예시나 단계별 설명 포함
- 필요시 추가 질문이나 관련 주제 제안
- 부적절하거나 위험한 내용에는 답변 거부

**면책 조항: 이 AI의 답변은 참고용이며, 중요한 결정이나 전문적인 조언이 필요한 경우에는 해당 분야 전문가와 상담하시기 바랍니다.**"""
    
    def create_query_prompt(
        self,
        question: str,
        context: List[Dict[str, Any]] = None,
        user_context: Dict[str, Any] = None,
        template_type: str = "query_basic"
    ) -> str:
        """질의응답용 프롬프트 생성"""
        try:
            # 컨텍스트 포맷팅
            context_text = ""
            if context:
                context_parts = []
                for i, ctx in enumerate(context, 1):
                    source_info = ""
                    if "metadata" in ctx:
                        meta = ctx["metadata"]
                        title = meta.get("title", "")
                        source = meta.get("source", "")
                        if title:
                            source_info = f" ({title})"
                        elif source:
                            source_info = f" (출처: {source})"
                    
                    context_parts.append(f"[참고자료 {i}]{source_info}\n{ctx['text']}")
                
                context_text = "\n\n".join(context_parts)
            
            # 사용자 컨텍스트 추가
            if user_context:
                additional_context = []
                if user_context.get("user_preference"):
                    additional_context.append(f"사용자 선호사항: {user_context['user_preference']}")
                if user_context.get("previous_topic"):
                    additional_context.append(f"이전 대화 주제: {user_context['previous_topic']}")
                
                if additional_context:
                    context_text = "\n".join(additional_context) + "\n\n" + context_text
            
            # 템플릿 선택 및 적용
            template = self.templates.get(template_type, self.templates["query_basic"])
            
            # 프롬프트 구성
            prompt = f"{self.system_prompt}\n\n{template.format(question=question, context=context_text)}"
            
            return prompt
            
        except Exception as e:
            logger.error(f"프롬프트 생성 실패: {e}")
            # 폴백 프롬프트
            return f"{self.system_prompt}\n\n질문: {question}\n\n답변:"
    
    def create_recommendation_prompt(
        self,
        user_history: List[Dict[str, Any]],
        related_content: List[Dict[str, Any]]
    ) -> str:
        """추천용 프롬프트 생성"""
        try:
            # 사용자 히스토리 포맷팅
            history_text = ""
            if user_history:
                history_parts = []
                for i, item in enumerate(user_history[-5:], 1):  # 최근 5개만
                    history_parts.append(f"{i}. {item.get('question', '')}")
                history_text = "\n".join(history_parts)
            
            # 관련 컨텐츠 포맷팅
            content_text = ""
            if related_content:
                content_parts = []
                for i, content in enumerate(related_content, 1):
                    title = content.get("metadata", {}).get("title", "")
                    category = content.get("metadata", {}).get("category", "")
                    text_preview = content.get("text", "")[:100] + "..."
                    
                    content_parts.append(f"{i}. [{category}] {title}\n   {text_preview}")
                content_text = "\n".join(content_parts)
            
            template = self.templates["recommendation"]
            prompt = template.format(
                user_history=history_text,
                related_content=content_text
            )
            
            return f"{self.system_prompt}\n\n{prompt}"
            
        except Exception as e:
            logger.error(f"추천 프롬프트 생성 실패: {e}")
            return f"{self.system_prompt}\n\n사용자에게 도움이 될 만한 주제들을 추천해주세요."
    
    def create_feedback_analysis_prompt(
        self,
        question: str,
        response: str,
        rating: int,
        feedback_text: Optional[str] = None
    ) -> str:
        """피드백 분석용 프롬프트 생성"""
        try:
            template = self.templates["feedback_analysis"]
            prompt = template.format(
                question=question,
                response=response,
                rating=rating,
                feedback_text=feedback_text or "추가 피드백 없음"
            )
            
            return f"{self.system_prompt}\n\n{prompt}"
            
        except Exception as e:
            logger.error(f"피드백 분석 프롬프트 생성 실패: {e}")
            return f"{self.system_prompt}\n\n다음 상호작용을 분석해주세요:\n질문: {question}\n평가: {rating}/5"
    
    def create_context_summary_prompt(self, documents: List[str]) -> str:
        """컨텍스트 요약용 프롬프트 생성"""
        try:
            docs_text = "\n\n---\n\n".join(documents)
            template = self.templates["context_summarization"]
            prompt = template.format(documents=docs_text)
            
            return f"{self.system_prompt}\n\n{prompt}"
            
        except Exception as e:
            logger.error(f"요약 프롬프트 생성 실패: {e}")
            return f"{self.system_prompt}\n\n다음 문서들을 요약해주세요:\n\n{documents[0] if documents else ''}"
    
    def add_custom_template(self, name: str, template: str) -> bool:
        """사용자 정의 템플릿 추가"""
        try:
            self.templates[name] = template
            logger.info(f"사용자 정의 템플릿 추가: {name}")
            return True
        except Exception as e:
            logger.error(f"템플릿 추가 실패: {e}")
            return False
    
    def get_template_list(self) -> List[str]:
        """사용 가능한 템플릿 목록 반환"""
        return list(self.templates.keys())
    
    def update_system_prompt(self, new_prompt: str) -> bool:
        """시스템 프롬프트 업데이트"""
        try:
            self.system_prompt = new_prompt
            logger.info("시스템 프롬프트 업데이트 완료")
            return True
        except Exception as e:
            logger.error(f"시스템 프롬프트 업데이트 실패: {e}")
            return False
    
    def create_multi_turn_prompt(
        self,
        conversation_history: List[Dict[str, str]],
        current_question: str,
        context: List[Dict[str, Any]] = None
    ) -> str:
        """다중 턴 대화용 프롬프트 생성"""
        try:
            # 대화 히스토리 포맷팅
            history_text = ""
            if conversation_history:
                history_parts = []
                for turn in conversation_history[-3:]:  # 최근 3턴만 유지
                    if turn.get("role") == "user":
                        history_parts.append(f"사용자: {turn['content']}")
                    elif turn.get("role") == "assistant":
                        history_parts.append(f"AI: {turn['content']}")
                
                history_text = "\n".join(history_parts)
            
            # 컨텍스트 포맷팅
            context_text = ""
            if context:
                context_parts = []
                for ctx in context:
                    context_parts.append(ctx.get("text", ""))
                context_text = "\n\n".join(context_parts)
            
            prompt = f"""{self.system_prompt}

이전 대화:
{history_text}

참고 자료:
{context_text}

현재 질문: {current_question}

답변:"""
            
            return prompt
            
        except Exception as e:
            logger.error(f"다중 턴 프롬프트 생성 실패: {e}")
            return self.create_query_prompt(current_question, context)
    
    def create_specialized_prompt(
        self,
        domain: str,
        question: str,
        context: List[Dict[str, Any]] = None
    ) -> str:
        """도메인별 특화 프롬프트 생성"""
        domain_prompts = {
            "medical": """의료 관련 질문에 답변할 때는 다음 사항을 반드시 준수하세요:
1. 의학적 조언이 아님을 명시
2. 전문의 상담 권유
3. 일반적인 정보만 제공
4. 자가 진단이나 치료 방법 제시 금지""",
            
            "legal": """법률 관련 질문에 답변할 때는 다음 사항을 준수하세요:
1. 법률 자문이 아님을 명시
2. 변호사 상담 권유
3. 일반적인 법률 정보만 제공
4. 구체적인 법률 해석이나 조언 금지""",
            
            "financial": """금융 관련 질문에 답변할 때는 다음 사항을 준수하세요:
1. 투자 조언이 아님을 명시
2. 전문가 상담 권유
3. 일반적인 금융 정보만 제공
4. 구체적인 투자 권유 금지""",
            
            "technical": """기술 관련 질문에 답변할 때는 다음 사항을 준수하세요:
1. 단계별 설명 제공
2. 코드 예시 포함 (필요시)
3. 대안 방법 제시
4. 보안 및 안전성 고려사항 언급"""
        }
        
        specialized_instruction = domain_prompts.get(domain, "")
        
        # 기본 프롬프트에 도메인별 지시사항 추가
        base_prompt = self.create_query_prompt(question, context)
        
        if specialized_instruction:
            return f"{base_prompt}\n\n도메인별 특별 지시사항:\n{specialized_instruction}"
        else:
            return base_prompt
    
    def validate_prompt_length(self, prompt: str, max_length: int = 4000) -> bool:
        """프롬프트 길이 검증"""
        return len(prompt) <= max_length
    
    def truncate_context(
        self,
        context: List[Dict[str, Any]],
        max_context_length: int = 2000
    ) -> List[Dict[str, Any]]:
        """컨텍스트 길이 제한"""
        truncated_context = []
        current_length = 0
        
        for ctx in context:
            text_length = len(ctx.get("text", ""))
            if current_length + text_length <= max_context_length:
                truncated_context.append(ctx)
                current_length += text_length
            else:
                # 남은 공간에 맞게 텍스트 자르기
                remaining_space = max_context_length - current_length
                if remaining_space > 100:  # 최소 100자는 남겨야 의미 있음
                    truncated_ctx = ctx.copy()
                    truncated_ctx["text"] = ctx["text"][:remaining_space] + "..."
                    truncated_context.append(truncated_ctx)
                break
        
        return truncated_context
    
    def get_prompt_stats(self) -> Dict[str, Any]:
        """프롬프트 매니저 통계"""
        return {
            "total_templates": len(self.templates),
            "template_names": list(self.templates.keys()),
            "system_prompt_length": len(self.system_prompt),
            "average_template_length": sum(len(t) for t in self.templates.values()) // len(self.templates)
        }
    
def create_query_prompt(user_input: str) -> str:
    """
    Generates a query prompt based on user input.
    """
    return f"Query: {user_input}"