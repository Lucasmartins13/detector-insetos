from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
import io
import base64
from PIL import Image

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
try:
    model = YOLO("best.pt")
    print("✅ Modelo carregado com sucesso!")
except Exception as e:
    print(f"❌ ERRO AO CARREGAR O MODELO: {e}")

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