from pathlib import Path
import math

class Obj:
    def __init__(self, filename: str):
        self.vertices   = []  # list[tuple[float,float,float]]
        self.texCoords  = []  # list[tuple[float,float]]
        self.normals    = []  # list[tuple[float,float,float]]
        self.faces      = []  # list[list[tuple(vi,ti,ni)]]

        self._positions = []  # expanded
        self._uvs       = []  # expanded
        self._normals   = []  # expanded
        self._bbox_min  = [ 1e9,  1e9,  1e9]
        self._bbox_max  = [-1e9, -1e9, -1e9]

        self._load(filename)
        
        # Si no hay normales, calcularlas
        if len(self.normals) == 0:
            print("⚠ Archivo OBJ sin normales, calculando...")
            self._compute_normals()
            print(f"✓ {len(self.normals)} normales calculadas")
        
        self._expand()

    # --------------- API pública para Model ----------------
    @property
    def positions(self): return self._positions
    @property
    def uvs(self):       return self._uvs
    @property
    def norms(self):     return self._normals

    @property
    def bbox_min(self):  return tuple(self._bbox_min)
    @property
    def bbox_max(self):  return tuple(self._bbox_max)

    # -------------------- Internals ------------------------
    def _load(self, filename: str):
        p = Path(filename)
        if not p.exists():
            raise FileNotFoundError(f"OBJ no encontrado: {filename}")

        with p.open("r", encoding="utf-8", errors="ignore") as f:
            for raw in f:
                if not raw or raw.startswith("#"): 
                    continue
                line = raw.strip()
                if not line:
                    continue

                parts = line.split()
                tag = parts[0]

                if tag == "v" and len(parts) >= 4:
                    x, y, z = map(float, parts[1:4])
                    self.vertices.append((x, y, z))
                    self._bbox_min[0] = min(self._bbox_min[0], x)
                    self._bbox_min[1] = min(self._bbox_min[1], y)
                    self._bbox_min[2] = min(self._bbox_min[2], z)
                    self._bbox_max[0] = max(self._bbox_max[0], x)
                    self._bbox_max[1] = max(self._bbox_max[1], y)
                    self._bbox_max[2] = max(self._bbox_max[2], z)

                elif tag == "vt":
                    if len(parts) >= 3:
                        u, v = map(float, parts[1:3])
                    elif len(parts) == 2:
                        u, v = float(parts[1]), 0.0
                    else:
                        continue
                    self.texCoords.append((u, v))

                elif tag == "vn" and len(parts) >= 4:
                    nx, ny, nz = map(float, parts[1:4])
                    self.normals.append((nx, ny, nz))

                elif tag == "f":
                    face = []
                    for comp in parts[1:]:
                        # soporta: v / v/t / v//n / v/t/n
                        v_idx, t_idx, n_idx = None, None, None
                        if "//" in comp:             # v//n
                            v_str, n_str = comp.split("//")
                            v_idx = int(v_str)
                            n_idx = int(n_str)
                        else:
                            trio = comp.split("/")
                            if len(trio) == 1:
                                v_idx = int(trio[0])
                            elif len(trio) == 2:
                                v_idx = int(trio[0])
                                t_idx = int(trio[1]) if trio[1] else None
                            elif len(trio) == 3:
                                v_idx = int(trio[0])
                                t_idx = int(trio[1]) if trio[1] else None
                                n_idx = int(trio[2]) if trio[2] else None
                        face.append((v_idx, t_idx, n_idx))
                    # Triangulamos si es quad o polígono convexo simple
                    if len(face) == 3:
                        self.faces.append(face)
                    elif len(face) >= 4:
                        v0 = face[0]
                        for i in range(1, len(face) - 1):
                            self.faces.append([v0, face[i], face[i+1]])

    def _compute_normals(self):
        """Calcular normales por vértice (promedio de normales de caras)"""
        # Inicializar acumuladores de normales para cada vértice
        vertex_normals = [[0.0, 0.0, 0.0] for _ in range(len(self.vertices))]
        vertex_counts = [0] * len(self.vertices)
        
        # Para cada cara (triángulo)
        for face in self.faces:
            # Obtener índices de vértices (convertir de 1-based a 0-based)
            v0_idx = face[0][0] - 1 if face[0][0] > 0 else len(self.vertices) + face[0][0]
            v1_idx = face[1][0] - 1 if face[1][0] > 0 else len(self.vertices) + face[1][0]
            v2_idx = face[2][0] - 1 if face[2][0] > 0 else len(self.vertices) + face[2][0]
            
            # Obtener posiciones de los vértices
            if not (0 <= v0_idx < len(self.vertices) and 
                    0 <= v1_idx < len(self.vertices) and 
                    0 <= v2_idx < len(self.vertices)):
                continue
                
            v0 = self.vertices[v0_idx]
            v1 = self.vertices[v1_idx]
            v2 = self.vertices[v2_idx]
            
            # Calcular dos vectores del triángulo
            edge1 = (v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2])
            edge2 = (v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2])
            
            # Producto cruz para obtener la normal de la cara
            nx = edge1[1] * edge2[2] - edge1[2] * edge2[1]
            ny = edge1[2] * edge2[0] - edge1[0] * edge2[2]
            nz = edge1[0] * edge2[1] - edge1[1] * edge2[0]
            
            # Normalizar
            length = math.sqrt(nx*nx + ny*ny + nz*nz)
            if length > 1e-8:
                nx /= length
                ny /= length
                nz /= length
            else:
                nx, ny, nz = 0.0, 0.0, 1.0
            
            # Acumular esta normal para cada vértice del triángulo
            for v_idx in [v0_idx, v1_idx, v2_idx]:
                vertex_normals[v_idx][0] += nx
                vertex_normals[v_idx][1] += ny
                vertex_normals[v_idx][2] += nz
                vertex_counts[v_idx] += 1
        
        # Promediar y normalizar
        for i in range(len(self.vertices)):
            if vertex_counts[i] > 0:
                nx = vertex_normals[i][0] / vertex_counts[i]
                ny = vertex_normals[i][1] / vertex_counts[i]
                nz = vertex_normals[i][2] / vertex_counts[i]
                
                length = math.sqrt(nx*nx + ny*ny + nz*nz)
                if length > 1e-8:
                    nx /= length
                    ny /= length
                    nz /= length
                else:
                    nx, ny, nz = 0.0, 0.0, 1.0
                    
                self.normals.append((nx, ny, nz))
            else:
                self.normals.append((0.0, 0.0, 1.0))
        
        # Actualizar las caras para que hagan referencia a las normales calculadas
        for face in self.faces:
            for i in range(len(face)):
                v_idx, t_idx, n_idx = face[i]
                # Convertir índice de vértice a índice de normal (1-based)
                if v_idx > 0:
                    n_idx = v_idx
                else:
                    n_idx = len(self.vertices) + v_idx + 1
                face[i] = (v_idx, t_idx, n_idx)

    def _fetch(self, arr, idx, default):
        if idx is None: return default
        # OBJ es 1-based y soporta negativos
        if idx > 0:  j = idx - 1
        else:        j = len(arr) + idx
        if 0 <= j < len(arr): return arr[j]
        return default

    def _expand(self):
        has_uv = len(self.texCoords) > 0
        has_n  = len(self.normals)  > 0

        for tri in self.faces:
            for (vi, ti, ni) in tri:
                px, py, pz = self._fetch(self.vertices, vi, (0.0,0.0,0.0))
                self._positions.append((px,py,pz))
                if has_uv:
                    u, v = self._fetch(self.texCoords, ti, (0.0,0.0))
                else:
                    u, v = 0.0, 0.0
                self._uvs.append((u, v))
                if has_n:
                    nx, ny, nz = self._fetch(self.normals, ni, (0.0,0.0,1.0))
                else:
                    nx, ny, nz = (0.0,0.0,1.0)
                self._normals.append((nx,ny,nz))