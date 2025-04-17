# Production build for Django storage service
FROM python:3.10-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Collect static files and apply migrations
RUN python manage.py collectstatic --noinput && \
    python manage.py migrate

# Use Gunicorn for serving
CMD ["gunicorn", "yourproject.wsgi:application", "--bind", "0.0.0.0:8000"]