FROM python:3.10-slim

WORKDIR /app

# Cài đặt các phụ thuộc hệ thống cần thiết
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    default-jdk\
    && rm -rf /var/lib/apt/lists/*

# Sao chép requirements.txt và cài đặt các gói Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ code vào container
COPY . .

# Lệnh chạy mặc định
CMD ["python", "main.py"]