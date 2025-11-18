import os
import sys
import pygame
from OpenGL import GL as gl
import glm
import math
import wave
import struct
from OpenGL.GL.shaders import compileProgram, compileShader

# Añadir rutas a los labs para reusar código
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LAB09_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "Lab_09", "RendererOpenGL2025"))
LAB10_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "Lab_10", "ModelViewer"))
if LAB09_DIR not in sys.path:
    sys.path.append(LAB09_DIR)
if LAB10_DIR not in sys.path:
    sys.path.append(LAB10_DIR)

from gl import Renderer
from model import Model
from vertexShaders import (
    vertex_shader,
    water_shader,
    twist_shader,
    pulse_shader,
    explode_shader,
    jelly_shader,
    spike_shader,
    melt_shader,
    fat_shader,
    glitch_vertex_shader,
)
from fragmentShaders import (
    fragment_shader,
    toon_shader,
    rainbow_shader,
    holographic_shader,
    glitch_shader,
    xray_shader,
    fire_shader,
    wireframe_shader,
    matrix_shader,
    disco_shader,
)

from orbit_camera import OrbitCamera
from env_skybox import EnvSkybox
from postprocess import PostProcessor
from post_shaders import POST_EFFECTS

# Configuración inicial
WIDTH, HEIGHT = 1280, 720
pygame.init()
pygame.display.set_caption("Proyecto 3 — Diorama")
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL)
clock = pygame.time.Clock()

gl.glDisable(gl.GL_CULL_FACE)

rend = Renderer(screen)
# cámara orbital del Lab_10 
cam = OrbitCamera(WIDTH, HEIGHT)
#rendar camera assigned earlier
rend.camera = cam

# Control de salida por consola: cambiar a True para debug extenso
VERBOSE = False

def project_print(*args, important: bool = False, **kwargs):
    """Imprime sólo si `VERBOSE` está activado o si el mensaje es importante.

    - important=True: siempre imprimir (errores / mensajes esenciales)
    - important=False: imprimir sólo si VERBOSE == True
    """
    if important or VERBOSE:
        print(*args, **kwargs)

# Luz
rend.pointLight = glm.vec3(2.0, 2.0, 2.0)

# Shaders iniciales
# definiendo listas para poder ciclar por índices
fragment_shaders = [
    ("Phong", fragment_shader),
    ("Toon", toon_shader),
    ("Rainbow", rainbow_shader),
    ("Holographic", holographic_shader),
    ("Glitch", glitch_shader),
    ("X-Ray", xray_shader),
    ("Fire", fire_shader),
    ("Wireframe", wireframe_shader),
    ("Matrix", matrix_shader),
    ("Disco", disco_shader),
]

# Shaders adicionales
advanced_lighting_shader = """
#version 330 core
in VS_OUT { vec2 uv; vec3 normal; vec3 worldPos; } fin;
out vec4 outColor;
uniform sampler2D uTexture0;
uniform bool uHasTexture;
uniform float uTime;
uniform float uEffectMix; // controlable por teclado

void main(){
    vec3 base = vec3(0.85, 0.8, 0.75);
    if(uHasTexture) base = texture(uTexture0, fin.uv).rgb;
    vec3 N = normalize(fin.normal);
    vec3 V = normalize(-fin.worldPos);
    vec3 L = normalize(vec3(0.4, 0.8, 0.3));
    float diff = max(dot(N, L), 0.0);
    // Blinn-Phong specular, shininess modulated by uEffectMix
    vec3 H = normalize(L + V);
    float spec = pow(max(dot(N, H), 0.0), mix(8.0, 64.0, clamp(uEffectMix, 0.0, 1.0)));
    vec3 rim = vec3(1.0) * pow(1.0 - max(dot(N, V), 0.0), 2.0) * 0.35 * uEffectMix;
    vec3 col = base * (0.2 + 0.8 * diff) + vec3(1.0) * spec * 0.6 + rim;
    outColor = vec4(col, 1.0);
}
"""

toon_rim_shader = """
#version 330 core
in VS_OUT { vec2 uv; vec3 normal; vec3 worldPos; } fin;
out vec4 outColor;
uniform sampler2D uTexture0;
uniform bool uHasTexture;
uniform float uTime;
uniform float uEffectMix;

void main(){
    vec3 base = vec3(0.9, 0.7, 0.6);
    if(uHasTexture) base = texture(uTexture0, fin.uv).rgb;
    vec3 N = normalize(fin.normal);
    vec3 L = normalize(vec3(-0.2, 1.0, 0.1));
    float d = dot(N, L);
    // quantizar iluminación en 3 niveles
    float q = d > 0.6 ? 1.0 : (d > 0.2 ? 0.6 : 0.2);
    float rim = pow(1.0 - max(dot(N, normalize(-fin.worldPos)), 0.0), 3.0) * 0.7 * uEffectMix;
    vec3 col = base * (0.15 + 0.85 * q) + vec3(1.0, 0.85, 0.7) * rim;
    outColor = vec4(col, 1.0);
}
"""

holo_adv_shader = """
#version 330 core
in VS_OUT { vec2 uv; vec3 normal; vec3 worldPos; } fin;
out vec4 outColor;
uniform sampler2D uTexture0;
uniform bool uHasTexture;
uniform float uTime;
uniform float uEffectMix;

void main(){
    vec2 u = fin.uv;
    float stripes = 0.5 + 0.5 * sin((fin.worldPos.x + fin.worldPos.z) * 6.0 + uTime * 2.0);
    vec3 base = mix(vec3(0.2,0.6,0.9), vec3(0.9,0.2,0.7), stripes * 0.5 + 0.25);
    if(uHasTexture){ base = mix(base, texture(uTexture0, u).rgb, 0.5); }
    // add subtle fresnel
    vec3 V = normalize(-fin.worldPos);
    float fres = pow(1.0 - max(dot(normalize(fin.normal), V), 0.0), 2.0);
    vec3 col = base * (0.25 + 0.75 * (0.5 + 0.5 * stripes)) + vec3(1.0) * fres * 0.6 * uEffectMix;
    outColor = vec4(col, 1.0);
}
"""

# Shader para lámpara
lamp_fragment_shader = """
#version 330 core
in VS_OUT { vec2 uv; vec3 normal; vec3 worldPos; } fin;
out vec4 outColor;
uniform sampler2D uTexture0;
uniform bool uHasTexture;
uniform float uTime;

void main(){
    vec3 base = vec3(1.0, 0.9, 0.6);
    if(uHasTexture){ base = texture(uTexture0, fin.uv).rgb; }
    // pulsado simple para dar sensación de latido
    float pulse = 0.6 + 0.4 * sin(uTime * 3.0);
    vec3 emiss = base * (0.6 + 1.2 * pulse);

    // iluminación simple con normal
    vec3 N = normalize(fin.normal);
    vec3 L = normalize(vec3(0.0, 1.0, 0.2));
    float diff = max(dot(N, L), 0.0);
    vec3 col = base * (0.2 + 0.8 * diff) + emiss;
    outColor = vec4(col, 1.0);
}
"""


vertex_shaders = [
    ("Default", vertex_shader),
    ("Water", water_shader),
    ("Twist", twist_shader),
    ("Pulse", pulse_shader),
    ("Explode", explode_shader),
    ("Jelly", jelly_shader),
    ("Spikes", spike_shader),
    ("Melt", melt_shader),
    ("Fat", fat_shader),
    ("GlitchV", glitch_vertex_shader),
]

# Carpet shaders
carpet_vertex_shader = """
#version 330 core

layout (location=0) in vec3 inPosition;
layout (location=1) in vec2 inTexCoord;
layout (location=2) in vec3 inNormal;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform float uTime;

out VS_OUT {
    vec2 uv;
    vec3 normal;
    vec3 worldPos;
} vout;

void main() {
    vec3 p = inPosition;
    // onda más marcada para simular que la alfombra se mueve con más vida
    float wave = sin((p.x + uTime * 1.2) * 2.0) * 0.06 + sin((p.z + uTime * 0.7) * 1.5) * 0.04;
    p.y += wave;

    vec4 wpos = modelMatrix * vec4(p, 1.0);
    vout.worldPos = wpos.xyz;
    vout.normal = mat3(modelMatrix) * inNormal;
    vout.uv = inTexCoord;
    gl_Position = projectionMatrix * viewMatrix * wpos;
}
"""

carpet_fragment_shader = """
#version 330 core

in VS_OUT {
    vec2 uv;
    vec3 normal;
    vec3 worldPos;
} fin;

out vec4 outColor;

uniform sampler2D uTexture0;
uniform bool      uHasTexture;
uniform float     uTime;

void main() {
    // desplazamiento UV para simular movimiento sobre la alfombra
    vec2 u = fin.uv;
    // aumento ligero del desplazamiento UV para dar sensación de movimiento
    vec2 uv_offset = vec2(
        0.024 * sin(uTime * 0.8 + fin.uv.y * 6.0),
        0.020 * cos(uTime * 0.9 + fin.uv.x * 5.0)
    );
    u += uv_offset;
    // patrón base: tonos cálidos (ámbar / dorado)
    vec3 border = vec3(0.78, 0.34, 0.12); // borde cálido
    vec3 center = vec3(0.96, 0.78, 0.35); // centro dorado

    // efecto de borde
    float bd = smoothstep(0.02, 0.15, min(min(u.x, 1.0 - u.x), min(u.y, 1.0 - u.y)));

    vec3 base = mix(border, center, bd);

    // detalles animados: swirl usando worldPos y tiempo
    float swirl = 0.5 + 0.5 * sin(fin.worldPos.x * 2.2 + fin.worldPos.z * 1.6 + uTime * 1.6 + u.x * 2.0);
    base *= 0.82 + 0.40 * swirl;

    // ruido sutil para variación de tono (suavizado) — no añadir brillos blancos
    float n = fract(sin(dot(fin.worldPos.xy + u * 6.0 , vec2(12.9898,78.233))) * 43758.5453 + uTime * 0.3);
    // aplicar una variación muy tenue al color para evitar zonas uniformes
    vec3 subtle = vec3(0.02) * n;

    // si hay textura, mezclarla con el patrón
    if (uHasTexture) {
        vec3 tex = texture(uTexture0, u).rgb;
        base = mix(base, tex, 0.55);
    }

    // iluminacion simple
    vec3 N = normalize(fin.normal);
    vec3 L = normalize(vec3(0.0, 1.0, 0.2));
    float diff = max(dot(N, L), 0.0);
    vec3 color = base * (0.3 + 0.7 * diff);
    // añadir la variación sutil (sin brillos blancos fuertes)
    color += subtle;

    outColor = vec4(color, 1.0);
}
"""

vertex_shaders.append(("CarpetV", carpet_vertex_shader))
fragment_shaders.append(("Carpet", carpet_fragment_shader))
fragment_shaders.append(("AdvancedLighting", advanced_lighting_shader))
fragment_shaders.append(("ToonRim", toon_rim_shader))
fragment_shaders.append(("HoloAdv", holo_adv_shader))
fragment_shaders.append(("Lamp", lamp_fragment_shader))
dynamic_vertex_shader = """
#version 330 core

layout (location=0) in vec3 inPosition;
layout (location=1) in vec2 inTexCoord;
layout (location=2) in vec3 inNormal;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform float uTime;

out VS_OUT {
    vec2 uv;
    vec3 normal;
    vec3 worldPos;
} vout;

void main(){
    vec3 p = inPosition;
    // deformación sutil en la dirección normal usando tiempo
    vec3 n = normalize(inNormal);
    float d = 0.03 * sin(uTime * 2.0 + p.x * 4.0 + p.z * 3.0);
    p += n * d;
    vec4 wpos = modelMatrix * vec4(p, 1.0);
    vout.worldPos = wpos.xyz;
    vout.normal = mat3(modelMatrix) * inNormal;
    vout.uv = inTexCoord;
    gl_Position = projectionMatrix * viewMatrix * wpos;
}
"""

vertex_shaders.append(("DynamicV", dynamic_vertex_shader))

# Skybox
_SKY = os.path.join(LAB09_DIR, "skybox")

def _find_face(name: str):
    for ext in ("png", "jpg", "jpeg"):
        p = os.path.join(_SKY, f"{name}.{ext}")
        if os.path.isfile(p):
            return p
    return None

faces = [
    _find_face("right"), _find_face("left"), _find_face("top"),
    _find_face("bottom"), _find_face("front"), _find_face("back"),
]

if all(faces):
    env = EnvSkybox(faces)
else:
    atlas_candidates = [
        os.path.join(_SKY, "custom_atlas.png"),
        os.path.join(_SKY, "custom_atlas.jpg"),
        os.path.join(_SKY, "custom_atlas.jpeg"),
        os.path.join(_SKY, "atlas.png"),
        os.path.join(_SKY, "atlas.jpg"),
    ]
    atlas_path = next((p for p in atlas_candidates if os.path.isfile(p)), None)
    if atlas_path:
        env = EnvSkybox(atlas_path)
    else:
        skybox_textures = [
            os.path.join(_SKY, "right.jpg"),
            os.path.join(_SKY, "left.jpg"),
            os.path.join(_SKY, "top.jpg"),
            os.path.join(_SKY, "bottom.jpg"),
            os.path.join(_SKY, "front.jpg"),
            os.path.join(_SKY, "back.jpg"),
        ]
        env = EnvSkybox(skybox_textures)
env.cameraRef = cam
rend.skybox = env

# Postprocessing
postfx = PostProcessor(WIDTH, HEIGHT)
rend.postprocess = postfx
post_effects = POST_EFFECTS
default_pp = "BloomSoft"
post_idx = next((i for i, (n, s) in enumerate(post_effects) if n == default_pp), 0)
postfx.set_effect(post_effects[post_idx][1])
project_print(f"PostProcess inicial: {post_effects[post_idx][0]}")
rend.effectMix = 0.5
shader_program_cache: dict[tuple[int,int], int] = {}

# Control de salida por consola: cambiar a True para debug extenso
VERBOSE = False

def project_print(*args, important: bool = False, **kwargs):
    """Imprime sólo si `VERBOSE` está activado o si el mensaje es importante.

    - important=True: siempre imprimir (errores / mensajes esenciales)
    - important=False: imprimir sólo si VERBOSE == True
    """
    if important or VERBOSE:
        print(*args, **kwargs)

def get_program(v_idx: int, f_idx: int):
    key = (v_idx, f_idx)
    if key in shader_program_cache:
        return shader_program_cache[key]
    try:
        v_src = vertex_shaders[v_idx][1]
        f_src = fragment_shaders[f_idx][1]
        vs = compileShader(v_src, gl.GL_VERTEX_SHADER)
        fs = compileShader(f_src, gl.GL_FRAGMENT_SHADER)
        prog = compileProgram(vs, fs)
        shader_program_cache[key] = prog
        project_print(f"Program compiled: V{v_idx} F{f_idx}")
        return prog
    except Exception as e:
        project_print(f"Error compilando programa V{v_idx} F{f_idx}: {e}", important=True)
        return None

# Música de fondo
def create_ambient_wav(path: str, duration_seconds: int = 12, sample_rate: int = 22050):
    if os.path.isfile(path):
        return
    project_print(f"Generando pista ambiental: {path}")
    amplitude = 10000  # 16-bit
    freq1 = 110.0
    freq2 = 220.0
    frames = []
    total_samples = duration_seconds * sample_rate
    for i in range(total_samples):
        t = i / sample_rate
        s = 0.5 * math.sin(2.0 * math.pi * freq1 * t + 0.5 * math.sin(2.0 * math.pi * 0.2 * t))
        s += 0.25 * math.sin(2.0 * math.pi * freq2 * t + 0.3 * math.sin(2.0 * math.pi * 0.15 * t))
        env = 0.5 + 0.5 * math.sin(math.pi * t / duration_seconds)
        val = int(max(-1.0, min(1.0, s * env)) * amplitude)
        frames.append(struct.pack('<h', val))
        frames.append(struct.pack('<h', val))

    try:
        with wave.open(path, 'wb') as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(b''.join(frames))
        project_print("Pista generada correctamente.")
    except Exception as e:
        project_print(f"Error creando WAV ambient: {e}", important=True)

music_path = os.path.join(BASE_DIR, 'music.wav')
create_ambient_wav(music_path)

music_enabled = False
def init_music(path):
    try:
        pygame.mixer.quit()
    except Exception:
        pass
    try:
        pygame.mixer.pre_init(22050, -16, 2, 1024)
        pygame.mixer.init()
        if os.path.isfile(path):
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.play(-1)
            project_print("Reproduciendo música de fondo (volume=0.6)")
            return True
        else:
            project_print(f"Archivo de música no encontrado después de crear: {path}", important=True)
            return False
    except Exception as e:
        project_print(f"No se pudo inicializar la música: {e}", important=True)
        return False

music_enabled = init_music(music_path)

# Cargar modelos y asignar posiciones
models_dir = os.path.join(LAB09_DIR, "models")
tex_dir = os.path.join(LAB09_DIR, "textures")

model_specs = [
    (os.path.join(models_dir, "Nijntje.obj"), os.path.join(tex_dir, "0000.jpg.jpeg")),
    (os.path.join(models_dir, "Pom Pom Purin 5.obj"), os.path.join(models_dir, "Body_color_4.png")),
    (os.path.join(models_dir, "choco cat.obj"), os.path.join(models_dir, "choco_cat_body_BaseColor.1001.png")),
    (os.path.join(models_dir, "Tuxedo Sam Character.obj"), None),
    (os.path.join(models_dir, "plane.obj"), None),
]

scene_models = []
for i, (obj_path, tex) in enumerate(model_specs):
    if not os.path.isfile(obj_path):
        continue
    m = Model(obj_path)
    if i == 0:
        # Nijntje - izquierda
        m.position = glm.vec3(-1.6, -0.4, -4.0)
        m.scale = glm.vec3(1.8)
    elif i == 1:
        # Pom Pom Purin - derecha
        m.position = glm.vec3(1.4, -0.35, -3.6)
        m.scale = glm.vec3(1.4)
    elif i == 2:
        # Choco cat - centro ligeramente adelante
        m.position = glm.vec3(0.0, -0.35, -3.8)
        m.scale = glm.vec3(1.2)
    elif i == 3:
        # Tuxedo Sam - detrás a la derecha
        m.position = glm.vec3(0.9, -0.45, -5.0)
        m.scale = glm.vec3(1.6)
    else:
        m.position = glm.vec3(0.0, -1.8, -4.0)
        m.scale = glm.vec3(5.0, 0.02, 5.0)  # alfombra

    try:
        if tex and os.path.isfile(tex):
            m.AddTexture(tex)
    except Exception:
        pass

    frag_idx = i % len(fragment_shaders)
    vert_idx = (i * 2) % len(vertex_shaders)

    floating = True
    if i == 2:
        floating = False
        vert_idx = 0

    scene_models.append({
        "model": m,
        "frag_idx": frag_idx,
        "vert_idx": vert_idx,
        "src": obj_path,
        "floating": floating,
    })
cam.target = glm.vec3(0.0, 0.0, -4.0)
cam.distance = 6.0

active_idx = 0

def create_carpet_texture(path: str, size: int = 512):
    if os.path.isfile(path):
        return
    try:
        surf = pygame.Surface((size, size), depth=32)
        surf.fill((40, 100, 230))
        border_color = (115, 20, 153)
        pygame.draw.rect(surf, border_color, (0, 0, size, size), 48)

        for i in range(6):
            center = (int(size * (0.2 + 0.12 * i)), int(size * (0.3 + 0.08 * (i % 3))))
            radius = int(size * (0.04 + 0.02 * (i % 4)))
            pygame.draw.circle(surf, (200, 180, 255), center, radius)

        for y in range(size):
            for x in range(size):
                dx = (x - size/2) / (size/2)
                dy = (y - size/2) / (size/2)
                d = (dx*dx + dy*dy)
                if d > 0.0:
                    shade = max(0, min(40, int(30 * (1.0 - d))))
                    r, g, b, = surf.get_at((x, y))[:3]
                    surf.set_at((x, y), (max(0, r - shade), max(0, g - shade), min(255, b + shade)))

        pygame.image.save(surf, path)
        project_print(f"Carpet texture created: {path}")
    except Exception as e:
        project_print(f"No se pudo crear textura de alfombra: {e}", important=True)

carpet_texture_path = os.path.join(BASE_DIR, "carpet_texture.png")
create_carpet_texture(carpet_texture_path)

for entry in scene_models:
    src = os.path.basename(entry.get("src", "")).lower()
    if "plane" in src:
        entry["vert_idx"] = len(vertex_shaders) - 1
        carpet_idx = next((idx for idx, (n, s) in enumerate(fragment_shaders) if n == "Carpet"), len(fragment_shaders) - 1)
        entry["frag_idx"] = carpet_idx
        try:
            entry["model"].AddTexture(carpet_texture_path)
        except Exception:
            pass
        project_print("Alfombra: shader y textura aplicados")
        break

design_candidates = [
    os.path.join(BASE_DIR, 'alfombra.png'),
    os.path.join(BASE_DIR, 'alfombra.jpg'),
    os.path.join(BASE_DIR, 'carpet_design.png'),
    os.path.join(BASE_DIR, 'carpet_design.jpg'),
    os.path.join(models_dir, 'alfombra.png'),
    os.path.join(models_dir, 'pajaro_azul.png'),
]
design_path = next((p for p in design_candidates if os.path.isfile(p)), None)
if design_path:
    for entry in scene_models:
        if 'plane' in os.path.basename(entry.get('src','')).lower():
            try:
                entry['model'].AddTexture(design_path)
                project_print(f"Aplicado diseño de alfombra desde: {design_path}")
            except Exception as e:
                project_print(f"No se pudo aplicar el diseño de alfombra: {e}", important=True)
            break

existing_srcs = {os.path.normpath(os.path.abspath(e.get("src", ""))) for e in scene_models}

pajaro_path = os.path.normpath(os.path.join(models_dir, "pajaro_azul.obj"))
if os.path.isfile(pajaro_path) and pajaro_path not in existing_srcs:
    try:
        mnew = Model(pajaro_path)
        ref_positions = [e['model'].position for e in scene_models if 'plane' not in os.path.basename(e.get('src','')).lower()]
        if ref_positions:
            avg_x = sum([p.x for p in ref_positions]) / len(ref_positions)
            avg_y = sum([p.y for p in ref_positions]) / len(ref_positions)
            avg_z = sum([p.z for p in ref_positions]) / len(ref_positions)
            mnew.position = glm.vec3(avg_x, avg_y + 2.2, avg_z - 2.5)
        else:
            mnew.position = glm.vec3(0.0, 1.6, -6.0)
        mnew.scale = glm.vec3(0.9)
        mnew._bird_base_x = mnew.position.x
        mnew._bird_base_y = mnew.position.y
        mnew._bird_base_z = mnew.position.z
        scene_models.append({
            "model": mnew,
            "frag_idx": (len(scene_models) + 1) % len(fragment_shaders),
            "vert_idx": (len(scene_models) * 2) % len(vertex_shaders),
            "src": pajaro_path,
            "floating": False,
        })
        project_print(f"OBJ añadido automáticamente a la escena: {os.path.basename(pajaro_path)}")
    except Exception as e:
        project_print(f"No se pudo añadir pajaro_azul.obj: {pajaro_path} {e}", important=True)
else:
    candidates = []
    for fn in os.listdir(models_dir):
        if fn.lower().endswith('.obj'):
            full = os.path.normpath(os.path.join(models_dir, fn))
            if full not in existing_srcs and os.path.basename(full).lower().startswith('subtool'):
                candidates.append(full)

    if candidates:
        max_add = 6
        added = 0
        x_step = 0.9
        ref_positions = [e['model'].position for e in scene_models if 'plane' not in os.path.basename(e.get('src','')).lower()]
        if ref_positions:
            avg_x = sum([p.x for p in ref_positions]) / len(ref_positions)
            avg_y = sum([p.y for p in ref_positions]) / len(ref_positions)
            avg_z = sum([p.z for p in ref_positions]) / len(ref_positions)
            x_start = avg_x + 1.6
        else:
            x_start = 2.0
            avg_y = -0.45
            avg_z = -3.8

        for new_obj in sorted(candidates):
            if added >= max_add:
                break
            try:
                mnew = Model(new_obj)
                px = x_start + added * x_step
                py = avg_y
                pz = avg_z
                mnew.position = glm.vec3(px, py, pz)
                mnew.scale = glm.vec3(0.9)
                scene_models.append({
                    "model": mnew,
                    "frag_idx": (len(scene_models) + 1) % len(fragment_shaders),
                    "vert_idx": (len(scene_models) * 2) % len(vertex_shaders),
                    "src": new_obj,
                })
                project_print(f"OBJ añadido automáticamente a la escena: {os.path.basename(new_obj)}")
                added += 1
            except Exception as e:
                project_print(f"No se pudo añadir OBJ automático: {new_obj} {e}", important=True)

lampara_path = os.path.normpath(os.path.join(models_dir, "lampara.obj"))
if os.path.isfile(lampara_path):
    fullp = os.path.normpath(lampara_path)
    if fullp not in existing_srcs:
        try:
            lamp = Model(lampara_path)
            lamp.scale = glm.vec3(0.9)
            lamp.rotation.x = 180.0
            lamp.position = glm.vec3(0.0, -1.2, -4.0)
            scene_models.append({
                "model": lamp,
                "frag_idx": len(fragment_shaders) - 1,
                "vert_idx": 0,
                "src": lampara_path,
                "emissive": True,
            })
            project_print(f"Lámpara añadida a la escena (emisiva): {os.path.basename(lampara_path)}")
        except Exception as e:
            project_print(f"No se pudo añadir lampara.obj: {e}", important=True)

def _model_half_height(m: 'Model'):
    try:
        bbmin = m.objFile.bbox_min
        bbmax = m.objFile.bbox_max
        extent_y = float(bbmax[1] - bbmin[1])
        extent_x = float(bbmax[0] - bbmin[0])
        extent_z = float(bbmax[2] - bbmin[2])
        largest = max(extent_x, extent_y, extent_z, 1e-6)
        desired = 1.5
        scale_factor = desired / largest
        half = (extent_y * 0.5) * scale_factor * float(m.scale.y)
        return half
    except Exception:
        return 0.5 * float(m.scale.y)


def snap_lamp_to_plane(mouse_pos):
    mx, my = mouse_pos
    origin, direction = screen_to_world_ray(mx, my, WIDTH, HEIGHT, rend.camera)
    plane_entry = None
    for e in scene_models:
        bn = os.path.basename(e.get('src','')).lower()
        if 'plane' in bn or 'alfombra' in bn or 'carpet' in bn:
            plane_entry = e
            break
    if plane_entry is None:
        print("No se encontró la alfombra para snapear la lámpara")
        return False

    plane_y = plane_entry['model'].position.y
    if abs(direction.y) < 1e-6:
        print("Rayo paralelo al plano, no se puede snapear la lámpara")
        return False
    t = (plane_y - origin.y) / direction.y
    hit = origin + direction * t

    for e in scene_models:
        if os.path.basename(e.get('src','')).lower().startswith('lampara'):
            lamp = e['model']
            lamp.position = glm.vec3(hit.x, plane_y + 0.45, hit.z)
            try:
                e['emissive'] = True
            except Exception:
                pass
            print(f"Lámpara posicionada en: {lamp.position.x:.2f}, {lamp.position.y:.2f}, {lamp.position.z:.2f}")
            return True

    print("No se encontró el modelo 'lampara' en la escena")
    return False

plane_entry = None
for e in scene_models:
    bn = os.path.basename(e.get('src','')).lower()
    if 'plane' in bn or 'alfombra' in bn or 'carpet' in bn:
        plane_entry = e
        break

if plane_entry is not None:
    plane_y = plane_entry['model'].position.y
    # colocar y ordenar los modelos encima de la alfombra
    arranged = [e for e in scene_models if not any(k in os.path.basename(e.get('src','')).lower() for k in ('plane','alfombra','carpet'))]
    bird_entry = next((x for x in scene_models if 'pajaro_azul' in os.path.basename(x.get('src','')).lower()), None)
    arranged_no_bird = [e for e in arranged if e is not bird_entry]

    center_x = plane_entry['model'].position.x
    base_z = plane_entry['model'].position.z + 0.2
    spacing_x = 1.6
    n = len(arranged_no_bird)
    for idx, e in enumerate(arranged_no_bird):
        m = e['model']
        ix = idx - (n - 1) / 2.0
        m.position.x = center_x + ix * spacing_x
        m.position.z = base_z
        half_h = _model_half_height(m)
        offset = 0.02
        m.position.y = plane_y + half_h + offset
        # alinear rotación para que todos miren hacia delante
        m.rotation.y = 0.0

    choc_entry = next((x for x in scene_models if 'choco' in os.path.basename(x.get('src','')).lower()), None)
    bird_entry = next((x for x in scene_models if 'pajaro_azul' in os.path.basename(x.get('src','')).lower()), None)
    if choc_entry and bird_entry:
        choc = choc_entry['model']
        bird = bird_entry['model']
        choc_half = _model_half_height(choc)
        bird_half = _model_half_height(bird)
        # alinear X/Z y poner en la parte superior de la cabeza
        bird.position.x = choc.position.x
        bird.position.z = choc.position.z
        bird.position.y = choc.position.y + choc_half + bird_half - 0.02
        bird_entry['floating'] = False
        bird._bird_base_x = bird.position.x
        bird._bird_base_y = bird.position.y
        bird._bird_base_z = bird.position.z
        print(f"Pájaro colocado sobre la cabeza de ChocoCat en: {bird.position.x:.2f},{bird.position.y:.2f},{bird.position.z:.2f}")

    try:
        name_to_idx = {n: idx for idx, (n, s) in enumerate(fragment_shaders)}
        mag_idx = name_to_idx.get('Magma', None)
        xray_idx = name_to_idx.get('X-Ray', None)
        if mag_idx is not None and xray_idx is not None:
            changed = 0
            for e in scene_models:
                if e.get('frag_idx') == mag_idx:
                    e['frag_idx'] = xray_idx
                    changed += 1
            if changed > 0:
                print(f"Reasignado shader 'Magma' -> 'X-Ray' en {changed} modelos")
    except Exception:
        pass

    try:
        name_to_idx = {n: idx for idx, (n, s) in enumerate(fragment_shaders)}
        glitch_idx = name_to_idx.get('Glitch', None)
        if glitch_idx is not None:
            tux_entry = next((x for x in scene_models if 'tuxedo' in os.path.basename(x.get('src','')).lower()), None)
            if tux_entry:
                prefer = name_to_idx.get('Holographic', name_to_idx.get('Phong', None))
                if prefer is not None:
                    tux_entry['frag_idx'] = prefer
                    print("Tuxedo: shader restaurado ->", fragment_shaders[prefer][0])
                    try:
                        name_to_v = {n: idx for idx, (n, s) in enumerate(vertex_shaders)}
                        default_v = name_to_v.get('Default', 0)
                        tux_entry['vert_idx'] = default_v
                        print(f"Tuxedo: vertex shader restaurado -> {vertex_shaders[default_v][0]}")
                    except Exception:
                        pass
                else:
                    orig_idx = 3 % len(fragment_shaders)
                    tux_entry['frag_idx'] = orig_idx
                    print(f"Tuxedo: shader restaurado por fallback -> {fragment_shaders[orig_idx][0]}")
                    try:
                        name_to_v = {n: idx for idx, (n, s) in enumerate(vertex_shaders)}
                        tux_entry['vert_idx'] = name_to_v.get('Default', 0)
                    except Exception:
                        pass
    except Exception:
        pass

    try:
        nij_entry = next((x for x in scene_models if 'nijntje' in os.path.basename(x.get('src','')).lower()), None)
        lamp_entry = next((x for x in scene_models if os.path.basename(x.get('src','')).lower().startswith('lampara')), None)
        if nij_entry and lamp_entry:
            try:
                name_to_idx = {n: idx for idx, (n, s) in enumerate(fragment_shaders)}
                xray_idx = name_to_idx.get('X-Ray', None)
                if xray_idx is not None:
                    nij_entry['frag_idx'] = xray_idx
                    print("Shader de Nijntje forzado a 'X-Ray'")
            except Exception:
                pass
            nij = nij_entry['model']
            lamp = lamp_entry['model']
            try:
                mouse_pos = pygame.mouse.get_pos()
                snapped = snap_lamp_to_plane(mouse_pos)
            except Exception:
                snapped = False

            if not snapped:
                nij_half = _model_half_height(nij)
                hand_offset = glm.vec3(0.25 * float(nij.scale.x), nij_half * 0.44, 0.16 * float(nij.scale.z))
                extra_down = 0.0 * float(nij.scale.y)
                lamp.position = glm.vec3(nij.position.x + hand_offset.x, nij.position.y + hand_offset.y - extra_down, nij.position.z + hand_offset.z)
                lamp.rotation.y = nij.rotation.y
                try:
                    lamp.scale = glm.vec3(1.4)
                except Exception:
                    pass
                lamp_entry['emissive'] = True
                print(f"Lámpara colocada en la mano de Nijntje en: {lamp.position.x:.2f},{lamp.position.y:.2f},{lamp.position.z:.2f}")

            try:
                plane_entry_local = plane_entry
                if plane_entry_local is not None:
                    plane_x = plane_entry_local['model'].position.x
                    plane_z = plane_entry_local['model'].position.z
                    plane_y = plane_entry_local['model'].position.y
                    front_z = plane_z + 1.3
                    lamp.position = glm.vec3(plane_x, plane_y + 0.58, front_z)
                    lamp.rotation.y = 0.0
                    try:
                        lamp.scale = glm.vec3(1.4)
                    except Exception:
                        pass
                    lamp_entry['emissive'] = True
                    print(f"Lámpara reposada al frente de la alfombra en: {lamp.position.x:.2f},{lamp.position.y:.2f},{lamp.position.z:.2f}")
            except Exception:
                pass
    except Exception as e:
        print("No se pudo posicionar la lámpara en la mano de Nijntje:", e)


def apply_common_uniforms(shader_program, rend):
    # tiempo
    loc_time = gl.glGetUniformLocation(shader_program, "uTime")
    if loc_time != -1:
        gl.glUniform1f(loc_time, rend.elapsedTime)

    loc_view = gl.glGetUniformLocation(shader_program, "viewMatrix")
    loc_proj = gl.glGetUniformLocation(shader_program, "projectionMatrix")
    if loc_view != -1:
        gl.glUniformMatrix4fv(loc_view, 1, gl.GL_FALSE, glm.value_ptr(rend.camera.viewMatrix))
    if loc_proj != -1:
        gl.glUniformMatrix4fv(loc_proj, 1, gl.GL_FALSE, glm.value_ptr(rend.camera.projectionMatrix))

    gl.glUniform3f(
        gl.glGetUniformLocation(shader_program, "uLightPos"),
        rend.pointLight.x, rend.pointLight.y, rend.pointLight.z,
    )
    gl.glUniform3f(
        gl.glGetUniformLocation(shader_program, "uViewPos"),
        rend.camera.position.x, rend.camera.position.y, rend.camera.position.z,
    )
    loc_mix = gl.glGetUniformLocation(shader_program, "uEffectMix")
    if loc_mix != -1:
        mix_val = getattr(rend, 'effectMix', 0.5)
        gl.glUniform1f(loc_mix, float(mix_val))


def screen_to_world_ray(mx: int, my: int, width: int, height: int, cam):
    ndc_x = (2.0 * mx) / width - 1.0
    ndc_y = 1.0 - (2.0 * my) / height
    near_clip = glm.vec4(ndc_x, ndc_y, -1.0, 1.0)
    far_clip = glm.vec4(ndc_x, ndc_y,  1.0, 1.0)
    inv = glm.inverse(cam.projectionMatrix * cam.viewMatrix)
    near_w = inv * near_clip
    far_w = inv * far_clip
    if abs(near_w.w) > 1e-6:
        near_w /= near_w.w
    if abs(far_w.w) > 1e-6:
        far_w /= far_w.w
    origin = glm.vec3(near_w.x, near_w.y, near_w.z)
    dir = glm.normalize(glm.vec3(far_w.x, far_w.y, far_w.z) - origin)
    return origin, dir


def snap_bird_to_plane(mouse_pos):
    mx, my = mouse_pos
    origin, direction = screen_to_world_ray(mx, my, WIDTH, HEIGHT, rend.camera)
    plane_entry = None
    for e in scene_models:
        bn = os.path.basename(e.get('src','')).lower()
        if 'plane' in bn or 'alfombra' in bn or 'carpet' in bn:
            plane_entry = e
            break
    if plane_entry is None:
        print("No se encontró la alfombra para snapear el pájaro")
        return False

    plane_y = plane_entry['model'].position.y
    if abs(direction.y) < 1e-6:
        print("Rayo paralelo al plano, no se puede snapear")
        return False
    t = (plane_y - origin.y) / direction.y
    if t < 0:
        pass
    hit = origin + direction * t

    for e in scene_models:
        if 'pajaro_azul' in os.path.basename(e.get('src','')).lower():
            bird = e['model']
            bird.position = glm.vec3(hit.x, plane_y + 0.18, hit.z)
            bird._bird_base_x = bird.position.x
            bird._bird_base_y = bird.position.y
            bird._bird_base_z = bird.position.z
            print(f"Pájaro posicionado en: {bird.position.x:.2f}, {bird.position.y:.2f}, {bird.position.z:.2f}")
            return True

    print("No se encontró el modelo 'pajaro_azul' en la escena")
    return False

# Loop principal
project_print(
    "\n=== CONTROLES: Proyecto 3 ===\n"
    "Mouse: arrastrar izq -> orbitar/elevación | rueda -> zoom\n"
    "Flechas: orbitar/elevación | Q/E: zoom\n"
    "1-7: ciclar fragment shader para el modelo 1..7\n"
    "A/D: cambiar modelo seleccionado | W/S: acercar/alejar cámara\n"
    "N/M: Siguiente/Anterior Fragment shader para modelo seleccionado\n"
    ",/. : Siguiente/Anterior Vertex shader para modelo seleccionado\n"
    "F: toggle wireframe | I: info | ESC: salir\n",
    important=True,
)

is_running = True
frame = 0
rotating = False
last_mouse = (0, 0)

while is_running:
    dt = clock.tick(60) / 1000.0
    rend.elapsedTime += dt
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                is_running = False
            elif event.key == pygame.K_f:
                rend.ToggleFilledMode()
            elif event.key == pygame.K_i:
                print(f"Frame: {frame} | FPS: {clock.get_fps():.1f}")
                print(f"Modelo seleccionado: {active_idx + 1} / {len(scene_models)}")
            elif event.key == pygame.K_b:
                mouse_pos = pygame.mouse.get_pos()
                ok = snap_bird_to_plane(mouse_pos)
                if ok:
                    print("Pájaro colocado en la posición del cursor sobre la alfombra.")
            elif event.key == pygame.K_l:
                mouse_pos = pygame.mouse.get_pos()
                ok = snap_lamp_to_plane(mouse_pos)
                if ok:
                    print("Lámpara colocada en la posición del cursor sobre la alfombra.")
            elif event.key == pygame.K_p:
                if music_enabled:
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.pause()
                        print("Música pausada")
                    else:
                        pygame.mixer.music.unpause()
                        print("Música reanudada")
            elif event.key == pygame.K_LEFTBRACKET:
                if music_enabled:
                    vol = max(0.0, pygame.mixer.music.get_volume() - 0.05)
                    pygame.mixer.music.set_volume(vol)
                    print(f"Volumen: {vol:.2f}")
            elif event.key == pygame.K_RIGHTBRACKET:
                if music_enabled:
                    vol = min(1.0, pygame.mixer.music.get_volume() + 0.05)
                    pygame.mixer.music.set_volume(vol)
                    print(f"Volumen: {vol:.2f}")
            elif event.key == pygame.K_a:
                active_idx = (active_idx + 1) % len(scene_models)
                try:
                    mpos = scene_models[active_idx]["model"].position
                    cam.target = mpos
                    half = _model_half_height(scene_models[active_idx]["model"])
                    cam.distance = max(3.0, float(half * 4.0))
                    print(f"Cámara enfocada en modelo {active_idx+1} -> {cam.target} (dist={cam.distance:.2f})")
                except Exception:
                    pass
            elif event.key == pygame.K_d:
                active_idx = (active_idx - 1) % len(scene_models)
                try:
                    mpos = scene_models[active_idx]["model"].position
                    cam.target = mpos
                    half = _model_half_height(scene_models[active_idx]["model"])
                    cam.distance = max(3.0, float(half * 4.0))
                    print(f"Cámara enfocada en modelo {active_idx+1} -> {cam.target} (dist={cam.distance:.2f})")
                except Exception:
                    pass
            elif event.key == pygame.K_w:
                cam.distance = max(cam.min_distance, cam.distance - 0.5)
                print(f"Cam.distance = {cam.distance:.2f}")
            elif event.key == pygame.K_s:
                # alejar cámara (back)
                cam.distance = min(cam.max_distance, cam.distance + 0.5)
                print(f"Cam.distance = {cam.distance:.2f}")
            elif event.key == pygame.K_n:
                scene_models[active_idx]["frag_idx"] = (scene_models[active_idx]["frag_idx"] + 1) % len(fragment_shaders)
            elif event.key == pygame.K_m:
                scene_models[active_idx]["frag_idx"] = (scene_models[active_idx]["frag_idx"] - 1) % len(fragment_shaders)
            elif event.key == pygame.K_COMMA:
                scene_models[active_idx]["vert_idx"] = (scene_models[active_idx]["vert_idx"] - 1) % len(vertex_shaders)
            elif event.key == pygame.K_PERIOD:
                scene_models[active_idx]["vert_idx"] = (scene_models[active_idx]["vert_idx"] + 1) % len(vertex_shaders)
            elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7):
                key_to_idx = {
                    pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2,
                    pygame.K_4: 3, pygame.K_5: 4, pygame.K_6: 5, pygame.K_7: 6,
                }
                idx = key_to_idx.get(event.key, 0)
                if idx < len(scene_models):
                    entry = scene_models[idx]
                    entry['frag_idx'] = (entry.get('frag_idx', 0) + 1) % len(fragment_shaders)
                    print(f"Modelo {idx+1} ('{os.path.basename(entry.get('src',''))}') -> shader: {fragment_shaders[entry['frag_idx']][0]}")
            elif (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]) and event.key == pygame.K_1:
                mild_names = ["Phong", "Toon", "Wireframe", "Matrix", "X-Ray"]
                name_to_index = {n: idx for idx, (n, s) in enumerate(fragment_shaders)}
                for i, entry in enumerate(scene_models):
                    name = mild_names[i % len(mild_names)]
                    entry["frag_idx"] = name_to_index.get(name, entry["frag_idx"])
                print("Modo shaders: Distinto aplicado (Ctrl+1)")
            elif (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]) and event.key == pygame.K_2:
                alt = ["Phong", "Toon"]
                name_to_index = {n: idx for idx, (n, s) in enumerate(fragment_shaders)}
                for i, entry in enumerate(scene_models):
                    entry["frag_idx"] = name_to_index.get(alt[i % 2], entry["frag_idx"])
                print("Modo shaders: Intercalado aplicado (Ctrl+2)")
            elif (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]) and event.key == pygame.K_3:
                name_to_v = {n: idx for idx, (n, s) in enumerate(vertex_shaders)}
                name_to_f = {n: idx for idx, (n, s) in enumerate(fragment_shaders)}
                candidates_f = ["AdvancedLighting", "ToonRim", "HoloAdv", "Phong", "Rainbow", "Holographic"]
                candidates_v = ["DynamicV", "Default", "Water", "Twist", "Pulse"]
                f_idxs = [name_to_f[n] for n in candidates_f if n in name_to_f]
                v_idxs = [name_to_v[n] for n in candidates_v if n in name_to_v]
                j = 0
                for e in scene_models:
                    bn = os.path.basename(e.get('src','')).lower()
                    if any(k in bn for k in ('plane','lampara','alfombra','carpet')):
                        continue
                    if len(f_idxs) > 0:
                        e['frag_idx'] = f_idxs[j % len(f_idxs)]
                    if len(v_idxs) > 0:
                        e['vert_idx'] = v_idxs[j % len(v_idxs)]
                    j += 1
                print("Asignadas combinaciones únicas de shaders a modelos (Ctrl+3)")
            elif event.key == pygame.K_z:
                if rend.postprocess is not None and post_effects:
                    post_idx = (post_idx + 1) % len(post_effects)
                    try:
                        rend.postprocess.set_effect(post_effects[post_idx][1])
                        print(f"PostProcess -> {post_effects[post_idx][0]}")
                    except Exception as e:
                        print("No se pudo cambiar postprocess:", e)
                else:
                    print("PostProcessor no disponible")
            elif event.key == pygame.K_c:
                rend.effectMix = max(0.0, rend.effectMix - 0.05)
                print(f"effectMix = {rend.effectMix:.2f}")
            elif event.key == pygame.K_x:
                rend.effectMix = min(1.0, rend.effectMix + 0.05)
                print(f"effectMix = {rend.effectMix:.2f}")

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                rotating = True
                last_mouse = event.pos
            elif event.button == 4:
                cam.zoom(-1.0)
            elif event.button == 5:
                cam.zoom(+1.0)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                rotating = False
        elif event.type == pygame.MOUSEMOTION and rotating:
            x, y = event.pos
            dx = x - last_mouse[0]
            dy = y - last_mouse[1]
            last_mouse = (x, y)
            cam.orbit_by(dx * 0.2, -dy * 0.2)

    # keyboard camera
    orbit_speed = 60.0
    elev_speed = 60.0
    zoom_speed = 2.0
    if keys[pygame.K_LEFT]:
        cam.azimuth_deg -= orbit_speed * dt
    if keys[pygame.K_RIGHT]:
        cam.azimuth_deg += orbit_speed * dt
    if keys[pygame.K_UP]:
        cam.elevation_deg += elev_speed * dt
    if keys[pygame.K_DOWN]:
        cam.elevation_deg -= elev_speed * dt
    if keys[pygame.K_q]:
        cam.distance = max(cam.min_distance, cam.distance - zoom_speed * dt)
    if keys[pygame.K_e]:
        cam.distance = min(cam.max_distance, cam.distance + zoom_speed * dt)

    cam.Update()

    for entry in scene_models:
        src = os.path.basename(entry.get("src", "")).lower()
        if "plane" in src:
            base_y = -1.8
            amp = 0.02
            freq = 0.8
            entry["model"].position.y = base_y + math.sin(rend.elapsedTime * freq) * amp
            break

    for entry in scene_models:
        src = os.path.basename(entry.get("src", "")).lower()
        if "pajaro_azul" in src:
            m = entry["model"]
            if not hasattr(m, "_bird_base_y"):
                m._bird_base_y = m.position.y
                m._bird_base_x = m.position.x
                m._bird_base_z = m.position.z

            if not entry.get("floating", True):
                m.position = glm.vec3(m._bird_base_x, m._bird_base_y, m._bird_base_z)
                m.rotation.y = 0.0
            else:
                v_amp = 0.4
                v_freq = 1.6
                h_amp = 0.6
                h_freq = 0.6
                m.position.y = m._bird_base_y + math.sin(rend.elapsedTime * v_freq) * v_amp
                m.position.x = m._bird_base_x + math.sin(rend.elapsedTime * h_freq) * h_amp
                # liger rotación lenta
                m.rotation.y = (rend.elapsedTime * 20.0) % 360.0
                # mantener ligeramente más atrás
                m.position.z = m._bird_base_z - 0.05 * math.sin(rend.elapsedTime * 0.9)
            break

    if rend.postprocess is not None and getattr(rend.postprocess, "ready", False):
        rend.postprocess.begin()
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    else:
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        gl.glViewport(0, 0, rend.width, rend.height)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        if rend.postprocess is not None and not getattr(rend.postprocess, "ready", False):
            print("[DEBUG] PostProcessor no está listo — usando backbuffer directo")

    # skybox
    if rend.skybox:
        gl.glDepthMask(gl.GL_FALSE)
        rend.skybox.Render()
        gl.glDepthMask(gl.GL_TRUE)

    for entry in scene_models:
        m = entry["model"]
        f_idx = entry["frag_idx"]
        v_idx = entry["vert_idx"]

        prog = get_program(v_idx, f_idx)
        if not prog:
            continue
        gl.glUseProgram(prog)
        apply_common_uniforms(prog, rend)

        modelMatrix = m.GetModelMatrix()
        loc_model = gl.glGetUniformLocation(prog, "modelMatrix")
        if loc_model != -1:
            gl.glUniformMatrix4fv(loc_model, 1, gl.GL_FALSE, glm.value_ptr(modelMatrix))

        loc_color = gl.glGetUniformLocation(prog, "uColor")
        if loc_color != -1:
            gl.glUniform3f(loc_color, 0.85, 0.85, 0.85)

        has_tex = (len(m.textures) > 0) and getattr(m, "_has_uv", False)
        loc_has_tex = gl.glGetUniformLocation(prog, "uHasTexture")
        if loc_has_tex != -1:
            gl.glUniform1i(loc_has_tex, gl.GL_TRUE if has_tex else gl.GL_FALSE)
        if has_tex:
            gl.glActiveTexture(gl.GL_TEXTURE0)
            gl.glBindTexture(gl.GL_TEXTURE_2D, m.textures[0])
            tloc = gl.glGetUniformLocation(prog, "uTexture0")
            if tloc != -1:
                gl.glUniform1i(tloc, 0)

        m.Render()

    if rend.postprocess is not None:
        rend.postprocess.draw(rend.elapsedTime)

    pygame.display.flip()
    frame += 1

pygame.quit()
