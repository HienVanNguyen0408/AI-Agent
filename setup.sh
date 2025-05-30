#!/bin/bash

echo "🚀 Bắt đầu thiết lập môi trường cho dự án..."

# 1. Tạo virtual environment nếu chưa có
if [ ! -d ".venv" ]; then
    echo "🔧 Tạo môi trường ảo (.venv)..."
    python3 -m venv .venv
fi

# 2. Kích hoạt môi trường ảo
source .venv/bin/activate

# 3. Cài đặt Poetry nếu chưa có
if ! command -v poetry &> /dev/null; then
    echo "📦 Cài đặt Poetry..."
    pip install poetry
fi

# 4. Cài dependencies từ pyproject.toml
echo "📦 Cài đặt dependencies..."
poetry install

# 5. Copy file config.yaml từ template nếu chưa có
if [ ! -f "config/config.yaml" ]; then
    echo "🛠️  Tạo file cấu hình config/config.yaml từ mẫu..."
    cp config/template.yaml config/config.yaml
fi

# 6. Tạo file .env từ example nếu chưa có
if [ ! -f ".env" ]; then
    echo "🛠️  Tạo file .env từ .env.example..."
    cp .env.example .env
fi

echo "✅ Hoàn tất setup! Sẵn sàng chạy dự án."
