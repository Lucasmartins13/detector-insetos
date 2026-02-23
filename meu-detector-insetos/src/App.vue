<template>
  <div id="app-wrapper">
    <header class="main-header">
      <div class="header-container">
        <img :src="img1" alt="Logo IFMG" class="header-logo" />
        <img :src="img2" alt="Logo IF Sertão" class="header-logo" />
      </div>
    </header>

    <main class="content">
      <div class="card">
        <h2 class="card-title">Detector de Insetos</h2>
        <p class="instructions">Selecione uma imagem para detecção automática.</p>
        
        <div class="upload-section">
          <input type="file" @change="onFileChange" accept="image/*" id="file-input" class="input-hidden" />
          <label for="file-input" class="btn-escolher">
            {{ selectedFile ? 'Trocar Imagem' : 'Escolher Arquivo' }}
          </label>
          
          <p v-if="selectedFile" class="file-info">{{ selectedFile.name }}</p>

          <button @click="uploadImage" :disabled="!selectedFile || loading" class="btn-detectar">
            {{ loading ? 'Analisando...' : 'Analisar Imagem' }}
          </button>
        </div>

        <div v-if="resultado" class="result-container">
          <div class="badge">
            {{ resultado.quantidade }} insetos encontrados
          </div>
          
          <div>
            <button @click="openModal" class="btn-visualizar">
              Visualizar Imagem Processada
            </button>
          </div>
        </div>
      </div>
    </main>

    <div v-if="showImage" class="overlay-result" @click.self="closeModal" @wheel.prevent>
      <div class="modal-content animate-zoom">
        <header class="modal-header">
          <div class="badge-modal">{{ resultado.quantidade }} Insetos Detectados</div>
          <button @click="closeModal" class="btn-fechar">X</button>
        </header>
        
        <div 
          class="image-preview-container" 
          ref="imageContainerRef" 
          @wheel="handleWheel"
          @mousedown="startDrag"
          @mousemove="onDrag"
          @mouseup="stopDrag"
          @mouseleave="stopDrag"
          :class="{ 'is-dragging': isDragging }"
        >
          <img 
            :src="resultado.imagem" 
            alt="Resultado da Detecção" 
            class="processed-img-modal"
            :style="{ transform: `translate(${translateX}px, ${translateY}px) scale(${scale})` }"
          />
        </div>
        
        <footer class="modal-footer">
          <p class="zoom-instruction">Use o scroll para dar zoom e <b>clique e arraste</b> para mover a imagem.</p>
          <button @click="closeModal" class="btn-voltar">Voltar para o Início</button>
        </footer>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';

import img1 from './assets/imagem1.png';
import img2 from './assets/imagem2.png';

const selectedFile = ref(null);
const resultado = ref(null);
const loading = ref(false);
const showImage = ref(false);

// --- Variáveis de Zoom e Posição ---
const scale = ref(1.0);
const translateX = ref(0);
const translateY = ref(0);
const imageContainerRef = ref(null);

// --- Variáveis para Arrastar (Pan) ---
const isDragging = ref(false);
const startX = ref(0);
const startY = ref(0);

// --- Funções Normais ---
const onFileChange = (e) => {
  selectedFile.value = e.target.files[0];
  resultado.value = null;
  showImage.value = false;
};

const uploadImage = async () => {
  loading.value = true;
  const formData = new FormData();
  formData.append('file', selectedFile.value);

  try {
    const response = await axios.post('http://127.0.0.1:8000/detectar', formData);
    resultado.value = response.data;
  } catch (error) {
    alert("Erro ao conectar com a API Python.");
  } finally {
    loading.value = false;
  }
};

// --- Controle do Modal ---
const openModal = () => {
  scale.value = 1.0;
  translateX.value = 0;
  translateY.value = 0;
  showImage.value = true;
};

const closeModal = () => {
  showImage.value = false;
};

// --- NOVA Lógica de Zoom no Mouse (Matemática centralizada) ---
const handleWheel = (event) => {
  if (!imageContainerRef.value) return;

  const rect = imageContainerRef.value.getBoundingClientRect();
  
  // Posição do mouse relativa ao CENTRO do container
  const mouseX = event.clientX - rect.left - rect.width / 2;
  const mouseY = event.clientY - rect.top - rect.height / 2;

  const direction = event.deltaY < 0 ? 1 : -1;
  const factor = 0.1;
  let newScale = scale.value + (direction * factor * scale.value);

  newScale = Math.min(Math.max(newScale, 0.5), 5.0);

  const scaleRatio = newScale / scale.value;
  translateX.value = mouseX - (mouseX - translateX.value) * scaleRatio;
  translateY.value = mouseY - (mouseY - translateY.value) * scaleRatio;

  scale.value = newScale;
};

// --- Lógica de Arrastar (Drag/Pan) ---
const startDrag = (event) => {
  isDragging.value = true;
  startX.value = event.clientX;
  startY.value = event.clientY;
};

const onDrag = (event) => {
  if (!isDragging.value) return;
  
  const dx = event.clientX - startX.value;
  const dy = event.clientY - startY.value;
  
  translateX.value += dx;
  translateY.value += dy;
  
  startX.value = event.clientX;
  startY.value = event.clientY;
};

const stopDrag = () => {
  isDragging.value = false;
};
</script>

<style>
/* RESET E GLOBAIS */
* { box-sizing: border-box; }
html, body { margin: 0 !important; padding: 0 !important; width: 100% !important; height: 100% !important; background-color: #38a13d !important; overflow: hidden; }
#app { margin: 0 !important; padding: 0 !important; max-width: 100% !important; width: 100% !important; display: block !important; }
#app-wrapper { display: flex; flex-direction: column; width: 100vw; height: 100vh; }

/* CABEÇALHO */
.main-header { background-color: #ffffff; width: 100%; height: 60px; display: flex; justify-content: flex-start; align-items: stretch; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin: 0; padding: 0; }
.header-container { display: flex; align-items: stretch; gap: 30px; padding-left: 15px; }
.header-logo { height: 100%; width: auto; object-fit: contain; display: block; }

/* CONTEÚDO */
.content { flex: 1; display: flex; justify-content: center; align-items: center; padding: 20px; }
.card { background: white; padding: 30px; border-radius: 15px; width: 100%; max-width: 450px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); text-align: center; }

/* ESTILOS GERAIS */
.card-title { color: #1b5e20; margin-top: 0; font-size: 1.4rem; }
.instructions { color: #333; margin-bottom: 20px; }
.btn-escolher { display: block; background: #f5f5f5; padding: 12px; border-radius: 8px; cursor: pointer; border: 1px dashed #38a13d; margin-bottom: 10px; font-weight: 500; }
.file-info { font-size: 0.85rem; color: #666; margin-bottom: 15px; }
.input-hidden { display: none; }
.btn-detectar { background-color: #1b5e20; color: white; border: none; padding: 15px; border-radius: 50px; width: 100%; cursor: pointer; font-weight: bold; font-size: 1.05rem; transition: background 0.3s; }
.btn-detectar:hover:not(:disabled) { background-color: #123e15; }
.btn-detectar:disabled { background-color: #a5d6a7; cursor: not-allowed; }
.badge { background: #38a13d; color: white; padding: 8px 20px; border-radius: 20px; margin: 20px 0; display: inline-block; font-weight: bold; font-size: 1.1rem; }
.btn-visualizar { background-color: #2e7d32; color: white; border: none; padding: 12px 25px; border-radius: 8px; cursor: pointer; font-weight: bold; transition: background 0.3s; }
.btn-visualizar:hover { background-color: #1b5e20; }

/* SOBREPOSIÇÃO (MODAL) */
.overlay-result {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
  background-color: rgba(0, 0, 0, 0.85); display: flex; justify-content: center; align-items: center;
  z-index: 2000; padding: 20px;
}
.modal-content {
  background: white; width: 95%; max-width: 900px; max-height: 90vh;
  border-radius: 20px; display: flex; flex-direction: column; overflow: hidden;
  box-shadow: 0 0 40px rgba(0,0,0,0.5);
}
.modal-header { padding: 15px 25px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; background: #fdfdfd; }
.badge-modal { background: #1b5e20; color: white; padding: 8px 20px; border-radius: 50px; font-weight: bold; }

/* BOTÃO DE FECHAR ATUALIZADO (X perfeitamente no centro) */
.btn-fechar { 
  background: #ff5252; 
  color: white; 
  border: none; 
  width: 35px; 
  height: 35px; 
  border-radius: 50%; 
  cursor: pointer; 
  font-weight: bold; 
  font-size: 1.1rem;
  display: flex; 
  justify-content: center; 
  align-items: center; 
  padding: 0;
}
.btn-fechar:hover { background: #d32f2f; }

/* CONTAINER E IMAGEM (ZOOM E PAN) */
.image-preview-container {
  flex: 1;
  overflow: hidden; 
  padding: 0; 
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f0f0f0;
  cursor: grab;
  position: relative;
}

.image-preview-container.is-dragging {
  cursor: grabbing;
}

/* IMAGEM ATUALIZADA (Sem o transform-origin antigo) */
.processed-img-modal {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  transition: transform 0.15s ease-out;
  pointer-events: none; 
}

.is-dragging .processed-img-modal {
  transition: none;
}

.modal-footer { padding: 15px; text-align: center; border-top: 1px solid #eee; background: #fdfdfd; }
.zoom-instruction { font-size: 0.9rem; color: #555; margin-bottom: 10px; margin-top: 0; }
.btn-voltar { background: #1b5e20; color: white; border: none; padding: 12px 30px; border-radius: 50px; cursor: pointer; font-weight: bold; }
.btn-voltar:hover { background: #123e15; }
.animate-zoom { animation: zoomIn 0.3s ease-out; }
@keyframes zoomIn { from { opacity: 0; transform: scale(0.9); } to { opacity: 1; transform: scale(1); } }
</style>