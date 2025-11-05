from __future__ import annotations

import ctypes
from typing import List

import pygame
from OpenGL import GL as gl
from OpenGL.GL.shaders import compileProgram, compileShader
import glm
import numpy as np


_VS = """
#version 330 core
layout (location = 0) in vec3 inPos;

uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;

out vec3 vTexCoord;

void main() {
    vTexCoord = inPos;
    mat4 vm = mat4(mat3(viewMatrix));
    vec4 clip = projectionMatrix * vm * vec4(inPos, 1.0);
    gl_Position = clip;
}
"""

_FS = """
#version 330 core
in vec3 vTexCoord;
out vec4 fragColor;
uniform samplerCube uSky;
void main() {
    fragColor = texture(uSky, normalize(vTexCoord));
}
"""


class EnvSkybox:
    def __init__(self, faces: List[str]):
        self.cameraRef = None

        # Cube vertices (NDC cube, no indices for simplicity)
        verts = np.array([
            -1.0,  1.0, -1.0,
            -1.0, -1.0, -1.0,
             1.0, -1.0, -1.0,
             1.0, -1.0, -1.0,
             1.0,  1.0, -1.0,
            -1.0,  1.0, -1.0,

            -1.0, -1.0,  1.0,
            -1.0, -1.0, -1.0,
            -1.0,  1.0, -1.0,
            -1.0,  1.0, -1.0,
            -1.0,  1.0,  1.0,
            -1.0, -1.0,  1.0,

             1.0, -1.0, -1.0,
             1.0, -1.0,  1.0,
             1.0,  1.0,  1.0,
             1.0,  1.0,  1.0,
             1.0,  1.0, -1.0,
             1.0, -1.0, -1.0,

            -1.0, -1.0,  1.0,
            -1.0,  1.0,  1.0,
             1.0,  1.0,  1.0,
             1.0,  1.0,  1.0,
             1.0, -1.0,  1.0,
            -1.0, -1.0,  1.0,

            -1.0,  1.0, -1.0,
             1.0,  1.0, -1.0,
             1.0,  1.0,  1.0,
             1.0,  1.0,  1.0,
            -1.0,  1.0,  1.0,
            -1.0,  1.0, -1.0,

            -1.0, -1.0, -1.0,
            -1.0, -1.0,  1.0,
             1.0, -1.0, -1.0,
             1.0, -1.0, -1.0,
            -1.0, -1.0,  1.0,
             1.0, -1.0,  1.0,
        ], dtype=np.float32)

        self.vao = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.vao)
        self.vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, verts.nbytes, verts, gl.GL_STATIC_DRAW)

        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 3 * 4, ctypes.c_void_p(0))
        gl.glBindVertexArray(0)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

        self.program = compileProgram(
            compileShader(_VS, gl.GL_VERTEX_SHADER),
            compileShader(_FS, gl.GL_FRAGMENT_SHADER)
        )

        # Cubemap texture
        self.cubemap = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, self.cubemap)
        for i, face in enumerate(faces):
            surf = pygame.image.load(face)
            data = pygame.image.tostring(surf, "RGB", False)
            gl.glTexImage2D(gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, gl.GL_RGB,
                            surf.get_width(), surf.get_height(), 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, data)

        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_R, gl.GL_CLAMP_TO_EDGE)
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, 0)

    def Render(self):
        if not self.program or not self.cameraRef:
            return

        gl.glUseProgram(self.program)
        gl.glUniformMatrix4fv(gl.glGetUniformLocation(self.program, "viewMatrix"), 1, gl.GL_FALSE, glm.value_ptr(self.cameraRef.viewMatrix))
        gl.glUniformMatrix4fv(gl.glGetUniformLocation(self.program, "projectionMatrix"), 1, gl.GL_FALSE, glm.value_ptr(self.cameraRef.projectionMatrix))

        gl.glDepthMask(gl.GL_FALSE)
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, self.cubemap)
        gl.glUniform1i(gl.glGetUniformLocation(self.program, "uSky"), 0)

        gl.glBindVertexArray(self.vao)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 36)
        gl.glBindVertexArray(0)

        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, 0)
        gl.glDepthMask(gl.GL_TRUE)
