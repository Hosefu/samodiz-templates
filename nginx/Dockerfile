FROM nginx:alpine

COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# Create directories for static files
RUN mkdir -p /usr/share/nginx/html/static /usr/share/nginx/html/media /usr/share/nginx/html/pdfs /usr/share/nginx/html/images && \
    chmod -R 777 /usr/share/nginx/html/static /usr/share/nginx/html/media /usr/share/nginx/html/pdfs /usr/share/nginx/html/images