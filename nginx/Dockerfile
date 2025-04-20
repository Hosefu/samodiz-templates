FROM nginx:alpine

COPY nginx/nginx.conf /etc/nginx/nginx.conf

# Create directories for static files
RUN mkdir -p /usr/share/nginx/html/static /usr/share/nginx/html/media \
    /usr/share/nginx/html/previews /usr/share/nginx/html/pdfs \
    /usr/share/nginx/html/images && \
    chmod -R 777 /usr/share/nginx/html/static /usr/share/nginx/html/media \
    /usr/share/nginx/html/previews /usr/share/nginx/html/pdfs \
    /usr/share/nginx/html/images