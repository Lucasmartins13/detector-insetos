#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$ROOT_DIR/meu-detector-insetos"

API_PORT=5555
FRONTEND_PORT=5556

cleanup() {
    echo ""
    echo "🛑 Encerrando serviços..."
    kill 0
}
trap cleanup EXIT INT TERM

echo "🚀 Subindo FastAPI na porta $API_PORT..."
cd "$ROOT_DIR"
uvicorn main:app --host 0.0.0.0 --port "$API_PORT" &

echo "🚀 Subindo frontend na porta $FRONTEND_PORT..."
cd "$FRONTEND_DIR"
npm run dev -- --port "$FRONTEND_PORT" --host &

echo ""
echo "✅ API:      http://127.0.0.1:$API_PORT"
echo "✅ Frontend: http://127.0.0.1:$FRONTEND_PORT"
echo "(Ctrl+C para encerrar ambos)"

wait
