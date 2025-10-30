import pygame
from pygame.locals import *
from OpenGL.GL import *
import glm

from gl import Renderer
from model import Model
from vertexShaders import *
from fragmentShaders import *

width = 960
height = 540

screen = pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.OPENGL)
pygame.display.set_caption("Lab 9: Shaders II")
clock = pygame.time.Clock()

glDisable(GL_CULL_FACE)

rend = Renderer(screen)
rend.pointLight = glm.vec3(2, 2, 2)

currVertexShader = vertex_shader
currFragmentShader = fragment_shader
rend.SetShaders(currVertexShader, currFragmentShader)

skyboxTextures = ["skybox/right.jpg", "skybox/left.jpg", "skybox/top.jpg",
                  "skybox/bottom.jpg", "skybox/front.jpg", "skybox/back.jpg"]
rend.CreateSkybox(skyboxTextures)

nijntjeModel = Model("models/Nijntje.obj")

try:
    nijntjeModel.AddTexture("textures/0000.jpg.jpeg")
except:
    pass

nijntjeModel.position = glm.vec3(0.0, -0.5, -4.0)
nijntjeModel.scale = glm.vec3(1.8, 1.8, 1.8)
nijntjeModel.rotation = glm.vec3(0.0, 180.0, 0.0)

rend.scene.append(nijntjeModel)

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
rotating = True
frame = 0

def change_fragment_shader(index):
    global current_frag_idx, currFragmentShader
    current_frag_idx = index % len(fragment_shaders)
    name, shader = fragment_shaders[current_frag_idx]
    currFragmentShader = shader
    rend.SetShaders(currVertexShader, currFragmentShader)
    print(f"Fragment: {name} ({current_frag_idx + 1})")

def change_vertex_shader(index):
    global current_vert_idx, currVertexShader
    current_vert_idx = index % len(vertex_shaders)
    name, shader = vertex_shaders[current_vert_idx]
    currVertexShader = shader
    rend.SetShaders(currVertexShader, currFragmentShader)
    print(f"Vertex: {name} ({current_vert_idx + 1})")

print("\n=== CONTROLES ===")
print("1-0: Fragment Shaders")
print("SHIFT+1-0: Vertex Shaders")
print("N/M: Siguiente/Anterior Fragment")
print(",/.: Siguiente/Anterior Vertex")
print("ESPACIO: Pausar rotación")
print("Flechas: Mover cámara")
print("WASD: Mover luz")
print("F: Wireframe | I: Info | ESC: Salir\n")

isRunning = True

while isRunning:
    deltaTime = clock.tick(60) / 1000
    rend.elapsedTime += deltaTime
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            isRunning = False
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                rend.ToggleFilledMode()
            elif event.key == pygame.K_SPACE:
                rotating = not rotating
            elif event.key == pygame.K_i:
                print(f"\nFrame: {frame} | FPS: {clock.get_fps():.1f}")
                print(f"Fragment: {fragment_shaders[current_frag_idx][0]}")
                print(f"Vertex: {vertex_shaders[current_vert_idx][0]}")
            
            elif event.key == pygame.K_n:
                change_fragment_shader(current_frag_idx + 1)
            elif event.key == pygame.K_m:
                change_fragment_shader(current_frag_idx - 1)
            
            elif event.key == pygame.K_COMMA:
                change_vertex_shader(current_vert_idx - 1)
            elif event.key == pygame.K_PERIOD:
                change_vertex_shader(current_vert_idx + 1)
            
            elif keys[K_LSHIFT] or keys[K_RSHIFT]:
                if event.key == pygame.K_1:   change_vertex_shader(0)
                elif event.key == pygame.K_2: change_vertex_shader(1)
                elif event.key == pygame.K_3: change_vertex_shader(2)
                elif event.key == pygame.K_4: change_vertex_shader(3)
                elif event.key == pygame.K_5: change_vertex_shader(4)
                elif event.key == pygame.K_6: change_vertex_shader(5)
                elif event.key == pygame.K_7: change_vertex_shader(6)
                elif event.key == pygame.K_8: change_vertex_shader(7)
                elif event.key == pygame.K_9: change_vertex_shader(8)
                elif event.key == pygame.K_0: change_vertex_shader(9)
            else:
                if event.key == pygame.K_1:   change_fragment_shader(0)
                elif event.key == pygame.K_2: change_fragment_shader(1)
                elif event.key == pygame.K_3: change_fragment_shader(2)
                elif event.key == pygame.K_4: change_fragment_shader(3)
                elif event.key == pygame.K_5: change_fragment_shader(4)
                elif event.key == pygame.K_6: change_fragment_shader(5)
                elif event.key == pygame.K_7: change_fragment_shader(6)
                elif event.key == pygame.K_8: change_fragment_shader(7)
                elif event.key == pygame.K_9: change_fragment_shader(8)
                elif event.key == pygame.K_0: change_fragment_shader(9)

    cam_speed = 3.0
    if keys[K_UP]:      rend.camera.position.z += cam_speed * deltaTime
    if keys[K_DOWN]:    rend.camera.position.z -= cam_speed * deltaTime
    if keys[K_RIGHT]:   rend.camera.position.x += cam_speed * deltaTime
    if keys[K_LEFT]:    rend.camera.position.x -= cam_speed * deltaTime
    if keys[K_PAGEUP]:  rend.camera.position.y += cam_speed * deltaTime
    if keys[K_PAGEDOWN]:rend.camera.position.y -= cam_speed * deltaTime

    light_speed = 5.0
    if keys[K_w]: rend.pointLight.z -= light_speed * deltaTime
    if keys[K_s]: rend.pointLight.z += light_speed * deltaTime
    if keys[K_a]: rend.pointLight.x -= light_speed * deltaTime
    if keys[K_d]: rend.pointLight.x += light_speed * deltaTime
    if keys[K_q]: rend.pointLight.y -= light_speed * deltaTime
    if keys[K_e]: rend.pointLight.y += light_speed * deltaTime

    if rotating:
        nijntjeModel.rotation.y += 30 * deltaTime

    rend.Render()
    pygame.display.flip()
    frame += 1

pygame.quit()