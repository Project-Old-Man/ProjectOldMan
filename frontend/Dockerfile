FROM nginx:alpine

# 정적 파일 복사 - 순서 중요!
COPY index.html /usr/share/nginx/html/
COPY app.js /usr/share/nginx/html/
COPY styles.css /usr/share/nginx/html/
COPY components/ /usr/share/nginx/html/components/
COPY images/ /usr/share/nginx/html/images/

# Nginx 설정 복사
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 권한 설정
RUN chmod -R 755 /usr/share/nginx/html/

# curl 설치 (헬스체크용)
RUN apk add --no-cache curl

# 포트 80 노출
EXPOSE 80

# 헬스체크 설정
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# nginx 실행
CMD ["nginx", "-g", "daemon off;"]
