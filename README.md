# RendererOpenGL2025
# Lab 9: Shaders II - Nijntje

## Archivos del Proyecto

- `RendererOpenGL2025.py` - Archivo principal
- `fragmentShaders.py` - 10 Fragment Shaders
- `vertexShaders.py` - 10 Vertex Shaders
- `gl.py` - Renderer
- `obj.py` - Cargador OBJ
- `model.py` - Clase Model
- `camera.py` - Cámara
- `buffer.py` - Buffer helper
- `skybox.py` - Skybox

## Controles

### Shaders
- 1-0: Fragment Shaders (efectos de color)
- SHIFT + 1-0: Vertex Shaders (efectos de geometría)
- N / M: Siguiente/Anterior Fragment Shader
- , / .: Siguiente/Anterior Vertex Shader

### Cámara
- Flechas (←→↑↓): Mover cámara en XZ
- PgUp / PgDn: Mover cámara en Y

### Luz
- W / S: Mover luz en Z
- A / D: Mover luz en X
- Q / E: Mover luz en Y

### Otros
- ESPACIO: Pausar/Reanudar rotación del modelo
- F: Toggle wireframe
- I: Mostrar información debug
- ESC: Salir

## Fragment Shaders (Color/Efectos)

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

## Vertex Shaders (Geometría/Animación)

| Tecla | Shader | Descripción |
|-------|--------|-------------|
| SHIFT+1 | Default | Sin modificación |
| SHIFT+2 | Water | Ondas de agua múltiples |
| SHIFT+3 | Twist | Torsión en espiral |
| SHIFT+4 | Pulse | Latido pulsante |
| SHIFT+5 | Explode | Desintegración |
| SHIFT+6 | Jelly | Movimiento gelatinoso |
| SHIFT+7 | Spikes | Cristalización con picos |
| SHIFT+8 | Melt | Derretirse hacia abajo |
| SHIFT+9 | Fat | Inflado animado |
| SHIFT+0 | Glitch | Desplazamiento glitch |

## Combinaciones Recomendadas

1. 4 + SHIFT+2 - Agua holográfica (futurista)
2. 3 + SHIFT+6 - Arcoíris gelatinoso (colorido)
3. 7 + SHIFT+8 - Fuego derretido (dramático)
4. 5 + SHIFT+0 - Glitch total (cyberpunk)
5. 0 + SHIFT+6 - Disco gelatina (divertido)

## Instalación

```
python RendererOpenGL2025.py
```

### Requisitos
- Python 3.x
- pygame
- PyOpenGL
- PyGLM
- PIL/Pillow

## Estructura de Carpetas

```
Lab_09/
├── RendererOpenGL2025.py
├── fragmentShaders.py
├── vertexShaders.py
├── gl.py
├── obj.py
├── model.py
├── camera.py
├── buffer.py
├── skybox.py
├── models/
│   └── Nijntje.obj
├── textures/
│   └── 0000.jpg.jpeg
└── skybox/
    ├── right.jpg
    ├── left.jpg
    ├── top.jpg
    ├── bottom.jpg
    ├── front.jpg
    └── back.jpg
```

## Características

- 20 shaders únicos (10 fragment + 10 vertex)
- 100 combinaciones posibles
- Animaciones fluidas con `uTime`
- Skybox integrado
- Sistema de iluminación Phong
- Rotación automática del modelo
- Información debug en tiempo real

## Capturas Sugeridas

Para tu entrega, captura estas combinaciones:

1. Shader 4 (Holographic) + SHIFT+2 (Water)
2. Shader 3 (Rainbow) + SHIFT+6 (Jelly)
3. Shader 7 (Fire) + SHIFT+8 (Melt)
4. Shader 5 (Glitch) + SHIFT+0 (Glitch)
5. Shader 1 (Phong) - para comparación

## Para la Entrega

Cumple con todos los requisitos del Lab 9:
- Mínimo 3 Vertex Shaders únicos → 10 incluidos
- Mínimo 3 Fragment Shaders únicos → 10 incluidos
- Sistema de cambio de shaders → Teclas 1-0 y SHIFT+1-0
- Efectos visuales diversos → Muy variados
- Uso de uniforms (uTime, luz, cámara) → Todos implementados

## Solución de Problemas

### El modelo no se ve
- Verifica que `models/Nijntje.obj` existe
- Presiona tecla 1 para shader Phong
- Presiona tecla F para toggle wireframe

### No hay textura
- Verifica que `textures/0000.jpg.jpeg` existe
- El modelo funciona sin textura (usa color sólido)

### No se ve el skybox
- Verifica que la carpeta `skybox/` tiene las 6 imágenes
- Nombres correctos: right.jpg, left.jpg, top.jpg, bottom.jpg, front.jpg, back.jpg

### Los shaders no cambian
- Verifica que `fragmentShaders.py` y `vertexShaders.py` están en el directorio
- Revisa la consola por errores de compilación

## Notas Técnicas

- OpenGL Version: 3.3 Core
- GLSL Version: 330 core
- FPS Target: 60 FPS
- Resolución: 960x540

