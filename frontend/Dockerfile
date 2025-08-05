FROM nginx:alpine

# 기본 nginx 설정 제거
RUN rm /etc/nginx/conf.d/default.conf

# 커스텀 nginx 설정 추가
COPY nginx.conf /etc/nginx/conf.d/

# 리팩토링된 파일들 복사
COPY index.html /usr/share/nginx/html/
COPY styles.css /usr/share/nginx/html/
COPY app.js /usr/share/nginx/html/

# components 폴더 전체 복사
COPY components/ /usr/share/nginx/html/components/

# images 폴더 전체 복사 (캐시 무효화를 위한 타임스탬프 추가)
COPY images/ /usr/share/nginx/html/images/

# 캐시 무효화를 위한 타임스탬프 파일 생성
RUN echo "$(date)" > /usr/share/nginx/html/images/cache_bust.txt

# 권한 설정
RUN chmod -R 755 /usr/share/nginx/html/

# 포트 80 노출
EXPOSE 80

# nginx 실행
CMD ["nginx", "-g", "daemon off;"]
