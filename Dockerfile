# ============================================================
# Etapa 1: compilar o frontend Vue (Vite) em arquivos estáticos
# ============================================================
FROM node:20-slim AS frontend

WORKDIR /app/frontend

# Instala dependências do Node primeiro (melhor cache)
COPY meu-detector-insetos/package*.json ./
RUN npm install

# Copia o restante do código do frontend e gera o build de produção
COPY meu-detector-insetos/ ./
RUN npm run build
# Resultado final fica em /app/frontend/dist


# ============================================================
# Etapa 2: backend FastAPI + YOLO servindo a interface web
# ============================================================
FROM python:3.11-slim

WORKDIR /app

# Bibliotecas de sistema exigidas pelo OpenCV (dependência do ultralytics)
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Instala o PyTorch em versão CPU-only (imagem bem menor que a versão CUDA padrão)
RUN pip install --no-cache-dir torch torchvision \
        --index-url https://download.pytorch.org/whl/cpu

# Instala as demais dependências Python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da API e o modelo treinado
COPY main.py best.pt ./

# Copia o frontend já compilado da etapa anterior
COPY --from=frontend /app/frontend/dist ./static

EXPOSE 5555

# Healthcheck usando o endpoint /health da API
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:5555/health').status==200 else 1)"

# Sobe a API (que também serve a interface web) automaticamente
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5555"]
