Lab 10 — Model Viewer

Requisitos
- Python 3.10–3.12 (64-bit)
- Windows: usar un venv y el mismo intérprete en VS Code

Instalación rápida
1) Crear y activar venv
   - PowerShell: python -m venv .venv; .\.venv\Scripts\Activate
2) Instalar dependencias
   - pip install -U pip
   - pip install -r Lab_10/requirements.txt

Ejecución
- python Lab_10/ModelViewer/ModelViewer.py

Controles
- Modelos: 1 / 2 / 3 (solo uno visible)
- Fragment shaders: N / M
- Vertex shaders: , / .
- Cámara teclado: ←/→ órbita, ↑/↓ elevación, Q/E zoom
- Cámara mouse: arrastrar botón izq (órbita/elevación), rueda (zoom)
- F: wireframe | I: info | ESC: salir

Notas
- Se reutiliza el renderer y shaders del Lab 09. El skybox está reimplementado (no el de clase).
- Si VS Code marca importaciones como no resueltas, selecciona el intérprete del venv (Python: Select Interpreter) o reinicia la ventana.

