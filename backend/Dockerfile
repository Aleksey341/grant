FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create directory for generated docs
RUN mkdir -p generated_docs fonts

# Download DejaVu font for Cyrillic PDF support
RUN python -c "\
import urllib.request, os; \
url = 'https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf'; \
[urllib.request.urlretrieve(url, f) for f in ['fonts/DejaVuSans.ttf']] if True else None; \
print('Font downloaded')" || echo "Font download skipped"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
