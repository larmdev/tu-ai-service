FROM python:3.13-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./src

WORKDIR /app/src

# ✅ เรียก main:app ตรงๆ (ไม่ต้องมี src. นำหน้าแล้ว เพราะเราอยู่ข้างในแล้ว)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000","--reload"]
