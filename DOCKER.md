# 🐳 Detector de Insetos no Docker

Toda a aplicação (API FastAPI + YOLO + interface web Vue) roda em **um único container**
que sobe sozinho. Todas as dependências (Python, PyTorch, ultralytics, Node para compilar
o frontend) são instaladas durante o build — não é preciso instalar nada na máquina, só o Docker.

## Como rodar

```bash
# Construir a imagem (na primeira vez baixa o PyTorch, pode demorar alguns minutos)
docker compose build

# Subir a aplicação
docker compose up
```

Depois acesse no navegador:

- **Interface web + API:** http://localhost:5555
- **Healthcheck/status da API:** http://localhost:5555/health

Para rodar em segundo plano:

```bash
docker compose up -d
```

Para parar:

```bash
docker compose down
```

## Como funciona

- **Etapa 1 (Node):** o `Dockerfile` compila o frontend Vue com `npm run build`, gerando
  arquivos estáticos.
- **Etapa 2 (Python):** instala as dependências e copia o `main.py`, o modelo `best.pt` e
  o frontend já compilado (pasta `static`).
- A própria API FastAPI serve a interface web **e** o endpoint `/detectar` na mesma porta
  (5555). Como tudo fica na mesma origem, não há problema de CORS.

> O modelo `best.pt` é copiado para dentro da imagem, então a detecção já vem pronta para uso.
