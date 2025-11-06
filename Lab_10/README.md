# RendererOpenGL2025

## Lab 10: Model Viewer
### Archivos del Proyecto

* ModelViewer.py — Archivo principal del laboratorio
* orbit_camera.py — Cámara orbital con control de mouse y teclado
* env_skybox.py — Skybox ambiental (nuevo, distinto al del Lab 9)
* model.py — Clase Model (manejo de transformaciones y texturas)
* obj.py — Cargador de modelos .obj con cálculo automático de normales
* vertexShaders.py — 10 Vertex Shaders (efectos geométricos y animaciones)
* fragmentShaders.py — 10 Fragment Shaders (efectos visuales y de color)
* postprocess.py — Sistema de post-proceso (framebuffer + efectos)
* post_shaders.py — Efectos de post-proceso (Pixelate, CRT, Bloom, etc.)
* skybox.py — Skybox base del Lab 9 (referencia)
* RendererOpenGL2025.py — Renderer del Lab 9 (reutilizado)

### Controles
Modelos

- W / S — Siguiente / Anterior modelo (.obj)

Solo un modelo visible a la vez

### Shaders

- 1–0 — Cambiar fragment shader

- SHIFT + 1–0 — Cambiar vertex shader

- N / M — Siguiente / Anterior fragment shader

- , / . — Siguiente / Anterior vertex shader

### Cámara

- Mouse: Arrastrar botón izquierdo → Órbita / elevación
- Teclado: ← / → → Órbita horizontal y ↑ / ↓ → Elevación vertical
- Q / E → Zoom In / Out
- Post-Proceso: Z / X — Siguiente / Anterior efecto de postproceso

Otros:
- F — Alternar wireframe
- I — Mostrar información (FPS, shader actual, modelo activo)
- ESC — Salir

### Modelos Incluidos
1. Nijntje.ob
2. Plane / Purin.obj	
3. Sphere / Custom.obj
   
### Fragment Shaders
Tecla	Shader	Descripción
- 1	Phong	Iluminación base realista
- 2	Toon	Estilo caricatura
- 3	Rainbow	Arcoíris animado
- 4	Holographic	Efecto brillante futurista
- 5	Glitch	Desplazamiento aleatorio
- 6	X-Ray	Rayos X translúcido
- 7	Fire	Fuego dinámico
- 8	Wireframe	Rejilla de modelo
- 9	Matrix	Código verde animado
- 0	Disco	Brillo colorido giratorio

### Efectos de Post-Proceso
- Z / X - Teclas
- Ciclar	Cambia entre efectos activos
- Pixelate	Bloques de píxeles
- BloomSoft	Iluminación difusa
- CRT	Simulación de pantalla antigua
- Duotone	Mezcla de tonos fríos/cálidos
- litchLines	Distorsión por líneas
- Kaleido6	Efecto caleidoscopio

### Instalación y Ejecución
```
python -m venv .venv
.\.venv\Scripts\Activate
pip install -U pip
pip install -r Lab_10/requirements.txt

python Lab_10/ModelViewer/ModelViewer.py
```
### Solución de Problemas
- El modelo no se ve:
-     Presiona F para alternar wireframe
-     Verifica que el .obj existe en models/

- El skybox no aparece
-     Asegúrate de tener las 6 imágenes (right, left, top, bottom, front, back)

### Notas Técnicas

* OpenGL Version: 3.3 Core
* GLSL Version: 330 core
* Resolución: 1280×720
* FPS Target: 60
* Renderer base: RendererOpenGL2025 (Lab 9)
* Skybox nuevo: EnvSkybox (Lab 10)