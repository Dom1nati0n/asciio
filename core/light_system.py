import numpy as np
import pygame
from dataclasses import dataclass

_BAYER4 = np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]], np.float32) / 16.0 - 0.5

@dataclass
class PointLight:
    wx: float
    wy: float
    radius: float
    intensity: float
    color: tuple = (255, 220, 140)
    lifetime: float = -1.0
    age: float = 0.0

class LightSystem:
    def __init__(self):
        self.lights: list[PointLight] = []
        self.flash: float = 0.0
        self.flash_col: np.ndarray = np.array([255, 255, 255], np.float32)
        self._surf: pygame.Surface | None = None

    def add(self, light: PointLight):
        self.lights.append(light)

    def remove(self, light: PointLight):
        if light in self.lights:
            self.lights.remove(light)

    def screen_flash(self, color=(255,255,255), intensity=1.0):
        self.flash = min(1.0, self.flash + intensity)
        self.flash_col = np.array(color, np.float32)

    def tick(self, dt: float):
        self.flash = max(0.0, self.flash - 3.0 * dt)
        i = 0
        while i < len(self.lights):
            l = self.lights[i]
            if l.lifetime > 0:
                l.age += dt
                if l.age >= l.lifetime:
                    del self.lights[i]
                    continue
            i += 1

    def apply(self, vp: pygame.Surface, extra_lights: list, cam_x: float, cam_y: float):
        rows, cols = vp.get_height() // 12, vp.get_width() // 7
        amb = np.array([2, 4, 8], np.float32) / 255.0
        lm = np.full((rows, cols, 3), amb, dtype=np.float32)

        for src in self.lights + extra_lights:
            vx = src.wx - cam_x
            vy = src.wy - cam_y
            r = int(src.radius) + 1
            x0 = max(0, int(vx - r))
            x1 = min(cols, int(vx + r + 1))
            y0 = max(0, int(vy - r))
            y1 = min(rows, int(vy + r + 1))
            if x0 >= x1 or y0 >= y1:
                continue

            XX, YY = np.meshgrid(np.arange(x0, x1, dtype=np.float32),
                                 np.arange(y0, y1, dtype=np.float32))
            dist = np.sqrt((XX - vx)**2 + (YY - vy)**2)

            # World-anchored Bayer dither
            dith = _BAYER4[
                (np.arange(y0, y1) + int(cam_y))[:, None] % 4,
                (np.arange(x0, x1) + int(cam_x))[None, :] % 4
            ] * 0.065

            bright = np.clip(
                src.intensity * (1.0 - (dist / max(src.radius, 0.001))**1.7) + dith,
                0.0, 1.0
            )

            lc = np.array(src.color, np.float32) / 255.0
            for c in range(3):
                lm[y0:y1, x0:x1, c] = np.minimum(1.0, lm[y0:y1, x0:x1, c] + bright * lc[c])

        if self.flash > 1e-3:
            lm = np.minimum(1.0, lm + self.flash * (self.flash_col / 255.0))

        lm = np.clip(lm, 0.0, 1.0)
        lm_u8 = (lm * 255).astype(np.uint8)
        lm_px = np.repeat(np.repeat(lm_u8, 12, axis=0), 7, axis=1)
        lm_t = np.ascontiguousarray(lm_px.transpose(1, 0, 2))

        if self._surf is None or self._surf.get_size() != vp.get_size():
            self._surf = pygame.Surface(vp.get_size())
        pygame.surfarray.blit_array(self._surf, lm_t)
        vp.blit(self._surf, (0, 0), special_flags=pygame.BLEND_RGB_MULT)