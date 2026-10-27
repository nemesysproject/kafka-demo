# ==============================================================================
# Multi-stage Dockerfile for Angular Dashboard
# ==============================================================================

# Stage 1: Build Angular application
FROM node:22-alpine AS builder

WORKDIR /app

COPY package.json ./
RUN npm install --legacy-peer-deps

COPY . .
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine AS runner

COPY --from=builder /app/dist/dashboard/browser /usr/share/nginx/html
# Fallback in case application builder outputs directly to dist/dashboard
RUN if [ ! -f /usr/share/nginx/html/index.html ]; then cp -r /app/dist/dashboard/* /usr/share/nginx/html/ || true; fi

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
