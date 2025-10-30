from __future__ import annotations

import pygame
from OpenGL.GL import *
import glm
import numpy as np
import ctypes

from obj import Obj


class Model(object):
    def __init__(self, objPath: str):
        # Transformaciones
        self.position = glm.vec3(0.0, 0.0, -5.0)
        self.rotation = glm.vec3(0.0, 0.0, 0.0)  # Euler (pitch, yaw, roll) en radianes
        self.scale    = glm.vec3(1.0, 1.0, 1.0)

        # Texturas (el renderer espera una lista)
        self.textureId = None
        self.textures: list[int] = []

        # Cargar OBJ (parser ya triangula y expande)
        self.objFile = Obj(objPath)

        # GPU buffers
        self.vao = 0
        self.vbo = 0
        self.ebo = 0
        self.vertex_count = 0
        self.index_count  = 0

        self._has_uv = False
        self._has_normals = False

        self._BuildBuffers()

    # --------------- Matrices ---------------
    def GetModel(self):
        return self.GetModelMatrix()

    def GetModelMatrix(self):
        # M = T * Rz * Ry * Rx * S  (recibe rotación en grados)
        T  = glm.translate(glm.mat4(1.0), self.position)
        Rx = glm.rotate(glm.mat4(1.0), glm.radians(self.rotation.x), glm.vec3(1, 0, 0))
        Ry = glm.rotate(glm.mat4(1.0), glm.radians(self.rotation.y), glm.vec3(0, 1, 0))
        Rz = glm.rotate(glm.mat4(1.0), glm.radians(self.rotation.z), glm.vec3(0, 0, 1))
        S  = glm.scale(glm.mat4(1.0), self.scale)
        return T * Rz * Ry * Rx * S

    def SetScale(self, s):
        if isinstance(s, (int, float)):
            self.scale = glm.vec3(s, s, s)
        else:
            self.scale = glm.vec3(s[0], s[1], s[2])

    def SetRotation(self, r):
        self.rotation = glm.vec3(r[0], r[1], r[2])

    def SetPosition(self, p):
        self.position = glm.vec3(p[0], p[1], p[2])

    # --------------- Texturas ---------------
    def AddTexture(self, path: str):
        surf = pygame.image.load(path)
        surf = pygame.transform.flip(surf, False, True)  # flip vertical para coords de OpenGL

        img_data = pygame.image.tostring(surf, "RGBA", True)
        w, h = surf.get_size()

        self.textureId = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.textureId)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        # compatibilidad con Renderer (usa model.textures[0])
        if self.textureId not in self.textures:
            self.textures.append(self.textureId)

        glBindTexture(GL_TEXTURE_2D, 0)

    # --------------- Render ---------------
    def Render(self):
        # El Renderer ya activa shader, setea matrices y texturas si existen.
        glBindVertexArray(self.vao)
        if self.index_count > 0:
            glDrawElements(GL_TRIANGLES, self.index_count, GL_UNSIGNED_INT, None)
        else:
            glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
        glBindVertexArray(0)

    # --------------- Interno: buffers ---------------
    def _BuildBuffers(self):
        # Datos EXPANDIDOS del parser
        verts_orig = self.objFile.vertices
        pos_exp    = list(self.objFile.positions)
        uv_exp     = list(self.objFile.uvs)
        nrm_exp    = list(self.objFile.norms)

        self._has_uv      = len(uv_exp)  == len(pos_exp) and len(uv_exp)  > 0
        self._has_normals = len(nrm_exp) == len(pos_exp) and len(nrm_exp) > 0

        # Centrar y escalar por AABB de vértices originales
        positions_np = np.array(verts_orig, dtype=np.float32) if len(verts_orig) > 0 else np.zeros((1,3), np.float32)
        bb_min = positions_np.min(axis=0)
        bb_max = positions_np.max(axis=0)
        center = (bb_min + bb_max) * 0.5
        extent = (bb_max - bb_min)
        largest = float(max(extent[0], extent[1], extent[2], 1e-6))

        desired = 1.5
        scale_factor = desired / largest

        pos_centered = []
        for (px, py, pz) in pos_exp:
            cx = (px - center[0]) * scale_factor
            cy = (py - center[1]) * scale_factor
            cz = (pz - center[2]) * scale_factor
            pos_centered.append((cx, cy, cz))

        # Empaquetar interleaved: P [T] [N]
        vertex_stride_floats = 3 + (2 if self._has_uv else 0) + (3 if self._has_normals else 0)
        packed = []
        for i in range(len(pos_centered)):
            px, py, pz = pos_centered[i]
            packed.extend([px, py, pz])
            if self._has_uv:
                u, v = uv_exp[i]
                packed.extend([u, v])
            if self._has_normals:
                nx, ny, nz = nrm_exp[i]
                packed.extend([nx, ny, nz])

        data = np.array(packed, dtype=np.float32)
        self.vertex_count = len(pos_centered)
        self.index_count = 0

        # Subir a GPU
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)

        stride_bytes = vertex_stride_floats * 4

        # location 0: position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride_bytes, ctypes.c_void_p(0))

        offset = 3 * 4
        # location 1: texcoord
        if self._has_uv:
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, stride_bytes, ctypes.c_void_p(offset))
            offset += 2 * 4

        # location 2: normal
        if self._has_normals:
            glEnableVertexAttribArray(2)
            glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, stride_bytes, ctypes.c_void_p(offset))

        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        # Info útil en consola
        try:
            print(f"Model: vertices={self.vertex_count}, has_uv={self._has_uv}, has_normals={self._has_normals}")
        except Exception:
            pass
