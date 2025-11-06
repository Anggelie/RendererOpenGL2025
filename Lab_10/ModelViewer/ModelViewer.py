import os
import sys
import pygame
from OpenGL import GL as gl
import glm

# Add Lab_09 module path to import renderer, model, and shaders
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Repo root assumed two levels up from this file
LAB09_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "..", "Lab_09", "RendererOpenGL2025"))
if LAB09_DIR not in sys.path:
    sys.path.append(LAB09_DIR)

from gl import Renderer  # type: ignore
from model import Model  # type: ignore
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
)  # type: ignore
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
)  # type: ignore

from orbit_camera import OrbitCamera
from env_skybox import EnvSkybox


def main():
    width, height = 1280, 720
    pygame.init()
    pygame.display.set_caption("Lab 10: Model Viewer")
    screen = pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.OPENGL)
    clock = pygame.time.Clock()

    gl.glDisable(gl.GL_CULL_FACE)

    rend = Renderer(screen)

    # Replace default camera with orbit camera focusing the model at origin
    cam = OrbitCamera(width, height)
    rend.camera = cam

    # Light
    rend.pointLight = glm.vec3(2.0, 2.0, 2.0)

    # Shaders from Lab 09
    currVertexShader = vertex_shader
    currFragmentShader = fragment_shader
    rend.SetShaders(currVertexShader, currFragmentShader)

    # Skybox (custom implementation, not the class from Lab 09)
    skybox_textures = [
        os.path.join(LAB09_DIR, "skybox", "right.jpg"),
        os.path.join(LAB09_DIR, "skybox", "left.jpg"),
        os.path.join(LAB09_DIR, "skybox", "top.jpg"),
        os.path.join(LAB09_DIR, "skybox", "bottom.jpg"),
        os.path.join(LAB09_DIR, "skybox", "front.jpg"),
        os.path.join(LAB09_DIR, "skybox", "back.jpg"),
    ]
    env = EnvSkybox(skybox_textures)
    env.cameraRef = cam
    rend.skybox = env

    # Model specs: pair each OBJ with an optional texture path.
    # You can replace paths below with your custom OBJ/texture.
    model_specs: list[tuple[str, str | None]] = [
        (os.path.join(LAB09_DIR, "models", "Nijntje.obj"), os.path.join(LAB09_DIR, "textures", "0000.jpg.jpeg")),
        (os.path.join(LAB09_DIR, "models", "plane.obj"), None),
        (os.path.join(LAB09_DIR, "models", "sphere.obj"), os.path.join(LAB09_DIR, "textures", "0000.jpg.jpeg")),
    ]

    # Detectar Pom Pom Purin automáticamente y usarlo como segundo modelo
    purin_obj = os.path.join(LAB09_DIR, "models", "Pom Pom Purin 5.obj")
    # Usa una difusa simple; otros mapas del repo no se usan en este renderer
    purin_tex = os.path.join(LAB09_DIR, "textures", "Body_color_4.png")
    if os.path.isfile(purin_obj):
        model_specs[1] = (purin_obj, purin_tex if os.path.isfile(purin_tex) else None)

    # If a custom OBJ exists at Lab_09/RendererOpenGL2025/models/Custom.obj, include it automatically
    custom_obj = os.path.join(LAB09_DIR, "models", "Custom.obj")
    custom_tex = os.path.join(LAB09_DIR, "textures", "Custom.png")
    if os.path.isfile(custom_obj):
        model_specs[-1] = (custom_obj, custom_tex if os.path.isfile(custom_tex) else None)

    # Load the models
    models: list[Model] = []
    for obj_path, tex in model_specs:
        m = Model(obj_path)
        m.position = glm.vec3(0.0, 0.0, 0.0)
        m.scale = glm.vec3(1.0, 1.0, 1.0)
        if tex and os.path.isfile(tex):
            try:
                m.AddTexture(tex)
            except Exception:
                pass
        models.append(m)

    active_idx = 0

    def set_active_model(idx: int):
        nonlocal active_idx
        active_idx = idx % len(models)
        rend.scene = [models[active_idx]]
        # Reset camera target (center) and keep distance
        cam.target = glm.vec3(0.0, 0.0, 0.0)

    set_active_model(0)

    # Shader lists for cycling like Lab 09
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
        ("Glitch", glitch_vertex_shader),
    ]

    current_frag_idx = 0
    current_vert_idx = 0

    def change_fragment_shader(index: int):
        nonlocal current_frag_idx, currFragmentShader
        current_frag_idx = index % len(fragment_shaders)
        name, shader = fragment_shaders[current_frag_idx]
        currFragmentShader = shader
        rend.SetShaders(currVertexShader, currFragmentShader)
        print(f"Fragment: {name} ({current_frag_idx + 1})")

    def change_vertex_shader(index: int):
        nonlocal current_vert_idx, currVertexShader
        current_vert_idx = index % len(vertex_shaders)
        name, shader = vertex_shaders[current_vert_idx]
        currVertexShader = shader
        rend.SetShaders(currVertexShader, currFragmentShader)
        print(f"Vertex: {name} ({current_vert_idx + 1})")

    print("\n=== CONTROLES (Lab 10) ===")
    print("W/S: Siguiente/Anterior Modelo (solo uno visible)")
    print("1-0: Seleccionar Fragment Shader | SHIFT+1-0: Vertex Shader")
    print("N/M: Siguiente/Anterior Fragment Shader")
    print(",/.: Siguiente/Anterior Vertex Shader")
    print("F: Wireframe | I: Info | ESC: Salir")
    print("Cámara (teclado): Flechas izquierda/derecha (órbita), flechas arriba/abajo (elevación), Q/E o Rueda (zoom)")
    print("Cámara (mouse): Arrastrar botón izq. (órbita/elevación), rueda (zoom)")

    # Mouse state for orbit
    rotating = False
    last_mouse = (0, 0)

    is_running = True
    frame = 0
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
                    print(f"\nFrame: {frame} | FPS: {clock.get_fps():.1f}")
                    print(f"Modelo activo: {active_idx + 1}")
                    print(f"Fragment: {fragment_shaders[current_frag_idx][0]}")
                    print(f"Vertex: {vertex_shaders[current_vert_idx][0]}")

                # Model switching with W/S
                elif event.key == pygame.K_w:
                    set_active_model(active_idx + 1)
                elif event.key == pygame.K_s:
                    set_active_model(active_idx - 1)

                # Shader switching like Lab 09
                elif event.key == pygame.K_n:
                    change_fragment_shader(current_frag_idx + 1)
                elif event.key == pygame.K_m:
                    change_fragment_shader(current_frag_idx - 1)
                elif event.key == pygame.K_COMMA:
                    change_vertex_shader(current_vert_idx - 1)
                elif event.key == pygame.K_PERIOD:
                    change_vertex_shader(current_vert_idx + 1)

                # Direct shader selection with number keys
                else:
                    # Map numeric key -> index 0..9
                    num_map = {
                        pygame.K_1: 0,
                        pygame.K_2: 1,
                        pygame.K_3: 2,
                        pygame.K_4: 3,
                        pygame.K_5: 4,
                        pygame.K_6: 5,
                        pygame.K_7: 6,
                        pygame.K_8: 7,
                        pygame.K_9: 8,
                        pygame.K_0: 9,
                    }
                    if event.key in num_map:
                        idx = num_map[event.key]
                        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                            change_vertex_shader(idx)
                        else:
                            change_fragment_shader(idx)

            # Mouse interactions
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    rotating = True
                    last_mouse = event.pos
                elif event.button == 4:  # wheel up
                    cam.zoom(-1.0)
                elif event.button == 5:  # wheel down
                    cam.zoom(+1.0)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    rotating = False
            elif event.type == pygame.MOUSEMOTION and rotating:
                x, y = event.pos
                dx = x - last_mouse[0]
                dy = y - last_mouse[1]
                last_mouse = (x, y)
                cam.orbit_by(dx * 0.2, -dy * 0.2)  # sensitivity

        # Keyboard camera control
        orbit_speed = 60.0  # deg/sec
        elev_speed = 60.0   # deg/sec
        zoom_speed = 2.0    # steps/sec

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

        # Update and render
        cam.Update()
        rend.Render()
        pygame.display.flip()
        frame += 1

    pygame.quit()


if __name__ == "__main__":
    main()
