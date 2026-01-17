FROM python:3.14-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./src

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

# FROM python:3.11-alpine

# WORKDIR /app

# # dependency สำหรับ build python packages
# RUN apk add --no-cache \
#     gcc \
#     musl-dev \
#     libffi-dev \
#     openssl-dev

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# COPY src ./src

# CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
