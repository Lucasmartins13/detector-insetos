from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from ultralytics import YOLO
import io
import os
import base64
from PIL import Image

try:
    import psutil
except ImportError:
    psutil = None

app = FastAPI()

# Configuração do CORS para permitir que o Vue.js acesse a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Carrega o modelo YOLO (certifique-se de que o best.pt está na mesma pasta)
print("⏳ Carregando o modelo YOLO...")
model = None
try:
    model = YOLO("best.pt")
    print("✅ Modelo carregado com sucesso!")
except Exception as e:
    print(f"❌ ERRO AO CARREGAR O MODELO: {e}")


@app.get("/health")
async def status():
    info = {
        "status": "ok" if model is not None else "erro",
        "modelo_carregado": model is not None,
    }

    if psutil is not None:
        mem = psutil.virtual_memory()
        processo = psutil.Process().memory_info().rss
        info["ram"] = {
            "processo_mb": round(processo / 1024 / 1024, 1),
            "sistema_usado_mb": round(mem.used / 1024 / 1024, 1),
            "sistema_total_mb": round(mem.total / 1024 / 1024, 1),
            "sistema_percentual": mem.percent,
        }
    else:
        info["ram"] = "psutil não instalado"

    return info

@app.post("/detectar")
async def detectar(file: UploadFile = File(...)):
    print("\n=======================================================")
    print(f"🟢 IMAGEM RECEBIDA: {file.filename}")
    
    try:
        # 1. Ler os bytes da imagem enviada pelo frontend
        print("Passo 1: Abrindo a imagem...")
        contents = await file.read()
        # .convert("RGB") é vital para evitar erro com PNGs transparentes!
        img = Image.open(io.BytesIO(contents)).convert("RGB")

        # 2. Realizar a detecção com o modelo
        print("Passo 2: Analisando com o YOLO (Pode demorar um pouco)...")
        results = model(img)
        result = results[0]
        quantidade = len(result.boxes)
        print(f"🔎 O YOLO encontrou {quantidade} insetos!")

        # 3. Gerar a imagem com as detecções
        print("Passo 3: Desenhando as caixinhas...")
        img_plotada = result.plot(labels=False, conf=False, line_width=2) 
        
        # 4. Converter o array do OpenCV/YOLO para imagem PIL e depois Base64
        print("Passo 4: Convertendo a imagem para mandar pro Vue...")
        img_pil = Image.fromarray(img_plotada[..., ::-1]) 
        
        buffer = io.BytesIO()
        img_pil.save(buffer, format="JPEG")
        img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")

        print("🚀 Sucesso! Devolvendo resultado para a tela.")
        print("=======================================================\n")

        # 5. Retornar JSON com a contagem e a imagem processada
        return {
            "quantidade": quantidade,
            "imagem": f"data:image/jpeg;base64,{img_str}"
        }

    except Exception as e:
        print(f"❌ ERRO DURANTE A ANÁLISE: {e}")
        return {"erro": str(e)}


# Serve a interface web (frontend Vue já compilado) na raiz, se existir.
# No Docker a pasta "static" é gerada a partir do build do Vite.
# As rotas da API (/health, /detectar) têm prioridade pois foram definidas acima.
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(STATIC_DIR):
    print(f"🌐 Servindo a interface web a partir de: {STATIC_DIR}")
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
else:
    print("ℹ️  Pasta 'static' não encontrada — rodando apenas a API (modo dev).")