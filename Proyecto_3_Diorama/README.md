## Proyecto_3_Diorama
## Diorama interactivo — Shaders y escena

## Archivos del Proyecto

- `main.py` - Archivo principal que carga la escena y gestiona la entrada y el render
- `model.py` - Clase `Model` (carga OBJ, bbox, texturas y render)
- `obj.py` - Cargador OBJ
- `gl.py` - Renderer y utilidades GL
- `postprocess.py` - PostProcessor (FBO + fullscreen passes)
- `post_shaders.py` - Shaders de postprocesado (Bloom, CRT, Glitch, etc.)
- `fragmentShaders.py` - Fragment shaders (color/efectos)
- `vertexShaders.py` - Vertex shaders (deformaciones/animaciones)
- `skybox.py` - Skybox / entorno
- `buffer.py` - Helpers de buffers
- `camera.py` / `orbit_camera.py` - Cámara orbital y utilidades
- `textures/` - Texturas usadas (alfombra, modelos, etc.)
- `models/` - Modelos OBJ incluidos (Nijntje, choco cat, Tuxedo, lampara, pajaro_azul, plane...)

## Controles

### Shaders
- `1..7`: Ciclar el fragment shader del modelo 1..7
- `N / M`: Siguiente / Anterior fragment shader para el modelo seleccionado
- `, / .`: Siguiente / Anterior vertex shader para el modelo seleccionado
- `CTRL + 1/2/3`: Aplicar presets de shaders (paletas estéticas predefinidas)

### Cámara / Selección
- `A / D`: Cambiar modelo seleccionado (la cámara enfoca el modelo seleccionado)
- `W / S`: Acercar / Alejar la cámara (ajusta `cam.distance`)
- Rueda del ratón: Zoom
- Click izquierdo + arrastrar: Orbitar alrededor de `cam.target`

### Post-process / efectos
- `Z`: Ciclar efectos de post-proceso (CRT, BloomSoft, Pixelate, etc.)
- `X / C`: Aumentar / Disminuir el `effectMix` global (controla parámetros visuales de algunos shaders)

### Colocación / utilidades
- `L`: Snapear la lámpara a la posición del cursor sobre la alfombra (si hay lámpara)
- `B`: Snapear el pájaro a la posición del cursor sobre la alfombra
- `F`: Alternar modo relleno / wireframe
- `I`: Mostrar información debug en consola (FPS, modelo seleccionado)
- `P`: Pausar / reanudar la música
- `ESC`: Salir

## Fragment Shaders (Color / Efectos)

| Tecla | Shader | Descripción |
|-------|--------|-------------|
| 1 | Phong | Iluminación clásica con especular (base realista) |
| 2 | Toon | Estilo cartoon / cel-shading |
| 3 | Rainbow | Colorido animado tipo arcoíris |
| 4 | Holographic | Efecto holográfico + fresnel |
| 5 | Glitch | Distorsión / desplazamientos tipo "glitch" |
| 6 | X-Ray | Efecto translúcido tipo rayos-X |
| 7 | Fire | Tonos de fuego y ruido animado |
| 8 | Wireframe | Grid / líneas sobre el modelo |
| 9 | Matrix | Estética "Matrix" (verde) |
| 0 | Disco | Bola disco colorida / cambios rápidos |

Adicionales incluidos en `main.py`: `AdvancedLighting`, `ToonRim`, `HoloAdv`, `Lamp`, `Carpet` (entre otros añadidos al listado de fragment shaders del proyecto).

## Vertex Shaders (Geometría / Animación)

| Tecla | Shader | Descripción |
|-------|--------|-------------|
| SHIFT+1 | Default | Sin modificación (transformación estándar) |
| SHIFT+2 | Water | Ondas/olas suaves |
| SHIFT+3 | Twist | Torsión en espiral |
| SHIFT+4 | Pulse | Latido / pulso temporal |
| SHIFT+5 | Explode | Desintegración / explosión controlada |
| SHIFT+6 | Jelly | Movimiento gelatinoso y blando |
| SHIFT+7 | Spikes | Apariencia con picos / cristales |
| SHIFT+8 | Melt | Efecto de derretimiento vertical |
| SHIFT+9 | Fat | Inflado dinámico |
| SHIFT+0 | GlitchV | Desplazamiento tipo glitch (vertex)

También hay un `DynamicV` y `CarpetV` para deformaciones sutiles (alfombra dinámica).

## Combinaciones Recomendadas

1. `Holographic` + `SHIFT+2` — Agua holográfica (futurista)
2. `Rainbow` + `SHIFT+6` — Arcoíris gelatinoso (colorido)
3. `Fire` + `SHIFT+8` — Fuego dramático (alto contraste)
4. `Glitch` + `SHIFT+0` — Estética cyberpunk
5. `Phong` + `Default` — Comparación "realista" para referencia

## Instalación

Ejecuta el proyecto desde la carpeta `Proyecto_3_Diorama`:

```powershell
python .\main.py
```

### Requisitos
- Python 3.x
- `pygame`
- `PyOpenGL`
- `PyGLM` (glm para Python)
- `Pillow` (opcional para manipular texturas)

Puedes instalarlos con pip si no los tienes:

```powershell
pip install pygame PyOpenGL PyGLM Pillow
```

## Estructura de Carpetas (resumen de `Proyecto_3_Diorama`)

```
Proyecto_3_Diorama/
├── main.py
├── model.py
├── obj.py
├── gl.py
├── postprocess.py
├── post_shaders.py
├── fragmentShaders.py
├── vertexShaders.py
├── orbit_camera.py
├── skybox.py
├── textures/
├── models/
└── README.md
```

## Características

- Colocación automática de modelos "sentados" sobre la alfombra (bbox-based)
- Shaders personalizados para alfombra (`Carpet`) y lámpara (`Lamp`) emisiva
- Post-processing con efectos (Bloom, CRT, Pixelate, GlitchLines, etc.) — tecla `Z` para ciclar
- Controles interactivos para cambiar shaders por modelo (1..7, N/M, ,/.)
- Snap functions: colocar lámpara y pájaro con `L` / `B` sobre la alfombra usando el cursor
- Presets de asignación de shaders (Ctrl+1/2/3) para paletas coherentes
- Generación procedural de textura de alfombra si no hay una imagen disponible
- Música ambiental generada/sonido de fondo (opcional)

## Solución de Problemas

### No aparece la escena / modelos no visibles
- Verifica que `models/` contiene los `.obj` esperados
- Revisa la consola por errores de compilación de shaders (mensajes "Error compilando programa ...")
- Presiona `F` para alternar wireframe y ver la geometría

### Shaders fallan al compilar
- La versión objetivo es GLSL `#version 330 core`. Si hay errores, mira la traza en consola e identifica el shader problemático.
- He corregido un caso típico (dot() entre vec3 y vec2) en `fragmentShaders.py` — revisa la consola para ver si aparece un error similar.

### La lámpara o pájaro no se colocan correctamente
- Usa `L` o `B` para snapearlos en runtime; si la alfombra no está detectada, esos comandos fallarán (comprueba nombre `plane`/`carpet` en `models/`).

### Problemas de audio
- Si no hay `music.wav`, el proyecto genera una pista simple. Revisa permisos y la inicialización de `pygame.mixer`.

## Notas Técnicas

- OpenGL Version: 3.3 Core
- GLSL Version: 330 core
- FPS Target: 60 FPS
- Resolución recomendada: 1280x720 (configurable)

---

Archivos principales
- `main.py`: ejecutable del diorama (usa el renderer de `Lab_09/RendererOpenGL2025` y la cámara orbital de `Lab_10/ModelViewer`).

Requisitos y notas
- Para ejecutar necesitas las dependencias de los labs (pygame, PyOpenGL, glm, etc.). Revisa `Lab_10/requirements.txt`.
- Este scaffold carga varios modelos desde `Lab_09/RendererOpenGL2025/models` y asigna shaders distintos a cada modelo.

Controles (por defecto)
- Mouse izquierdo (arrastrar): orbitar / elevar
- Rueda del mouse: zoom
- Flechas: orbitar/elevación (teclado)
- `Q` / `E`: acercar/alejar (zoom por teclado)
- `1`..`5`: enfocar la cámara en el modelo correspondiente (cada número apunta a una posición del diorama)
- `W` / `S`: siguiente / anterior modelo activo (cambia qué modelo es el objetivo del selector)
- `N` / `M`: siguiente / anterior fragment shader para el modelo seleccionado
- `,` / `.`: siguiente / anterior vertex shader para el modelo seleccionado
- `Ctrl+1`: asignar un shader distinto (paleta suave) a cada modelo (modo "distinto")
- `Ctrl+2`: intercalar entre dos shaders (modo "intercalado")
- `F`: alternar wireframe
- `I`: imprimir info (FPS, shader activo)
- `ESC`: salir

La alfombra mágica: el `plane.obj` ahora tiene una textura procedural y se mueve ligeramente en Y simulando vuelo. Puedes ajustar la velocidad/amplitud en `Proyecto_3_Diorama/main.py` (variables `freq` y `amp`).

Música de fondo
- Se reproduce automáticamente una pista ambiental en bucle (si no existe `Proyecto_3_Diorama/music.wav` se genera una pista corta procedural llamada `music.wav`).
- Controles de audio:
	- `P`: pausar / reanudar música
	- `[` / `]`: bajar / subir volumen

Si prefieres usar tu propia canción, coloca un archivo `music.wav` dentro de `Proyecto_3_Diorama/`.

## Fragment Shaders (Color / Efectos)

| Tecla | Shader | Descripción |
|-------|--------|-------------|
| 1 | Phong | Iluminación realista con specular |
| 2 | Toon | Estilo cartoon con outline |
| 3 | Rainbow | Efecto arcoíris animado |
| 4 | Holographic | Efecto holográfico futurista |
| 5 | Glitch | Efecto glitch digital/cyberpunk |
| 6 | X-Ray | Efecto rayos X translúcido |
| 7 | Fire | Efecto de fuego realista |
| 8 | Wireframe | Grid sobre el modelo |
| 9 | Matrix | Código Matrix verde |
| 0 | Disco | Bola disco con colores |

### Efectos de Post-Proceso
- Z / X - Teclas
- Ciclar: Cambia entre efectos activos
- Pixelate: Bloques de píxeles
- BloomSoft: Iluminación difusa
- CRT: Simulación de pantalla antigua
- Duotone: Mezcla de tonos fríos/cálidos
- litchLines: Distorsión por líneas
- Kaleido6: Efecto caleidoscopio

### Uso
1. Abrir un terminal en la raíz del workspace.
2. (Opcional) crear/activar un entorno Python e instalar dependencias:
```powershell
python -m venv venv; .\venv\Scripts\Activate.ps1
pip install -r Lab_10\requirements.txt
```
3. Ejecutar:
```powershell
python Proyecto_3_Diorama\main.py
```
