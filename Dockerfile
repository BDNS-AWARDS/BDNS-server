# Dockerfile
# Django 최상위 루트에서 작성

# Base Image 설정
FROM python:3.11

# 작업 디렉토리 설정
WORKDIR /app

# requirements.txt에 명시된 필요한 packages 설치
COPY ./requirements.txt requirements.txt

# 필요한 패키지 설치
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 현재 디렉토리의 모든 파일을 Docker 이미지 내부로 복사
COPY . .

RUN pip install gunicorn

# Gunicorn 실행
CMD ["sh", "-c", "python manage.py migrate && gunicorn --bind 0.0.0.0:8000 config.wsgi:application"]