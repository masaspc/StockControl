FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# IPAexゴシック フォントと必要パッケージ
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    fonts-ipaexfont \
    libldap2-dev \
    libsasl2-dev \
    && rm -rf /var/lib/apt/lists/*

# IPAexゴシック フォントへのシンボリックリンク（ReportLab 用）
RUN mkdir -p /fonts && \
    ln -sf /usr/share/fonts/opentype/ipaexfont-gothic/ipaexg.ttf /fonts/ipaexg.ttf || true

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
