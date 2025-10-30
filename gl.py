"""
OpenGL renderer glue: manages active program, camera uniforms,
scene draw, and skybox. Clean prints and time uniform support.
"""

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import glm
from skybox import Skybox


class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()

        glViewport(0, 0, self.width, self.height)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glClearColor(0.2, 0.2, 0.25, 1.0)

        self.camera = None
        self.scene = []
        self.skybox = None

        self.activeShader = None
        self.value = 0.0
        self.elapsedTime = 0.0
        self.pointLight = glm.vec3(1, 1, 1)

        from camera import Camera
        self.camera = Camera(self.width, self.height)

    def SetShaders(self, vertex_shader_source, fragment_shader_source):
        try:
            vertex_shader = compileShader(vertex_shader_source, GL_VERTEX_SHADER)
            fragment_shader = compileShader(fragment_shader_source, GL_FRAGMENT_SHADER)
            self.activeShader = compileProgram(vertex_shader, fragment_shader)
            print("✓ Shaders compilados correctamente")
        except Exception as e:
            print("✗ Error compilando shaders:", e)
            self.activeShader = None

    def CreateSkybox(self, faces):
        self.skybox = Skybox(faces)
        self.skybox.cameraRef = self.camera
        print("✓ Skybox creado correctamente")

    def ToggleFilledMode(self):
        polygonMode = glGetIntegerv(GL_POLYGON_MODE)
        if polygonMode[1] == GL_FILL:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    def Render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        self.camera.Update()

        # ========== DIBUJAR SKYBOX PRIMERO (al fondo) ==========
        if self.skybox:
            # Desactivar escritura en depth buffer para que todo se dibuje "encima"
            glDepthMask(GL_FALSE)
            self.skybox.Render()
            glDepthMask(GL_TRUE)

        # ========== DIBUJAR MODELOS (al frente) ==========
        if not self.activeShader:
            return

        # Activar shader y pasar matrices comunes
        glUseProgram(self.activeShader)

        # Tiempo para shaders animados (si se declara)
        loc_time = glGetUniformLocation(self.activeShader, "uTime")
        if loc_time != -1:
            glUniform1f(loc_time, self.elapsedTime)

        loc_view = glGetUniformLocation(self.activeShader, "viewMatrix")
        loc_proj = glGetUniformLocation(self.activeShader, "projectionMatrix")
        glUniformMatrix4fv(loc_view, 1, GL_FALSE, glm.value_ptr(self.camera.viewMatrix))
        glUniformMatrix4fv(loc_proj, 1, GL_FALSE, glm.value_ptr(self.camera.projectionMatrix))

        # Luz y cámara
        glUniform3f(glGetUniformLocation(self.activeShader, "uLightPos"),
                    self.pointLight.x, self.pointLight.y, self.pointLight.z)
        glUniform3f(glGetUniformLocation(self.activeShader, "uViewPos"),
                    self.camera.position.x, self.camera.position.y, self.camera.position.z)

        # Dibujar cada modelo de la escena
        for model in self.scene:
            modelMatrix = model.GetModelMatrix()
            loc_model = glGetUniformLocation(self.activeShader, "modelMatrix")
            glUniformMatrix4fv(loc_model, 1, GL_FALSE, glm.value_ptr(modelMatrix))

            # Color base (si no hay textura)
            glUniform3f(glGetUniformLocation(self.activeShader, "uColor"), 0.85, 0.85, 0.85)

            # Textura (solo si hay UVs)
            has_tex = (len(model.textures) > 0) and getattr(model, "_has_uv", False)
            glUniform1i(glGetUniformLocation(self.activeShader, "uHasTexture"), GL_TRUE if has_tex else GL_FALSE)
            if has_tex:
                glActiveTexture(GL_TEXTURE0)
                glBindTexture(GL_TEXTURE_2D, model.textures[0])
                glUniform1i(glGetUniformLocation(self.activeShader, "uTexture0"), 0)

            # Dibujar
            model.Render()