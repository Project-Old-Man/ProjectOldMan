FROM nginx:alpine

# 정적 파일 복사
COPY . /usr/share/nginx/html

# Nginx 설정 복사 (있는 경우)
# COPY nginx.conf /etc/nginx/nginx.conf

# 포트 노출
EXPOSE 80

# 헬스체크
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# Nginx 실행
CMD ["nginx", "-g", "daemon off;"]
COPY images/ /usr/share/nginx/html/images/

# 캐시 무효화를 위한 타임스탬프 파일 생성
RUN echo "$(date)" > /usr/share/nginx/html/images/cache_bust.txt

# 권한 설정
RUN chmod -R 755 /usr/share/nginx/html/

# 포트 80 노출
EXPOSE 80

# nginx 실행
CMD ["nginx", "-g", "daemon off;"]
