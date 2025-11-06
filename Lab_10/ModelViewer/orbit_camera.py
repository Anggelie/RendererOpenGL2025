import glm


class OrbitCamera:
    def __init__(self, width: int, height: int):
        self.screenWidth = width
        self.screenHeight = height

        self.target = glm.vec3(0.0, 0.0, 0.0)
        self.distance = 4.0
        self.min_distance = 1.2
        self.max_distance = 12.0

        self.azimuth_deg = 180.0  
        self.elevation_deg = 15.0  
        self.min_elev = -80.0
        self.max_elev = 80.0

        self.position = glm.vec3(0.0, 0.0, 0.0)
        self.viewMatrix = glm.mat4(1.0)
        self.projectionMatrix = None
        self.CreateProjectionMatrix(60.0, 0.1, 1000.0)

    def CreateProjectionMatrix(self, fov: float, nearPlane: float, farPlane: float):
        aspect = max(self.screenWidth / max(self.screenHeight, 1), 1e-6)
        self.projectionMatrix = glm.perspective(glm.radians(fov), aspect, nearPlane, farPlane)

    def orbit_by(self, d_azimuth_deg: float, d_elev_deg: float):
        self.azimuth_deg += d_azimuth_deg
        self.elevation_deg += d_elev_deg
        self.elevation_deg = max(self.min_elev, min(self.max_elev, self.elevation_deg))

    def zoom(self, steps: float):
        self.distance += steps * 0.25
        self.distance = max(self.min_distance, min(self.max_distance, self.distance))

    def Update(self):
        az = glm.radians(self.azimuth_deg)
        el = glm.radians(self.elevation_deg)
        r = self.distance

        x = r * glm.cos(el) * glm.cos(az)
        z = r * glm.cos(el) * glm.sin(az)
        y = r * glm.sin(el)

        self.position = glm.vec3(self.target.x + x, self.target.y + y, self.target.z + z)
        self.viewMatrix = glm.lookAt(self.position, self.target, glm.vec3(0.0, 1.0, 0.0))

