# ============================================================
# Money Hunter Frontend — Dockerfile
# Maintainer: Young-cheol (Backend Engineer)
# ============================================================

# ── Stage 1: Build (Node.js) ──────────────────────────────
FROM node:20-alpine AS builder
WORKDIR /app

# 의존성 설치 (캐시 활용)
COPY package.json package-lock.json ./
RUN npm ci

# 소스 코드 복사 및 빌드
COPY . .
RUN npm run build

# ── Stage 2: Serve (Nginx) ────────────────────────────────
FROM nginx:alpine

# 빌드 결과물(dist)을 Nginx 웹 루트로 복사
COPY --from=builder /app/dist /usr/share/nginx/html

# Nginx 설정 (SPA 라우팅 지원을 위해 필요 시 추가 설정)
# 여기서는 기본 정적 파일 서빙만 수행
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
