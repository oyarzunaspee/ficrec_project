FROM python:3.11-slim

RUN apt-get update && apt-get install -y nodejs npm nginx && apt-get clean

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend and frontend
COPY backend backend
COPY frontend frontend
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# Build frontend
WORKDIR /app/frontend
RUN npm install && npm run build

# Collect static
WORKDIR /app
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh
RUN python backend/manage.py collectstatic --noinput

EXPOSE 80
CMD ["./entrypoint.sh"]
