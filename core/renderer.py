import numpy as np
import pygame
from .glyph_atlas import GlyphAtlas
from .light_system import LightSystem
from .sonar import Sonar

class Renderer:
    def __init__(self, cfg, atlas: GlyphAtlas, light_sys: LightSystem):
        self.cfg = cfg
        self.atlas = atlas
        self.light_sys = light_sys

        self.layer = pygame.Surface((cfg.internal_w, cfg.internal_h))
        self.palette = np.array(cfg.palette, dtype=np.uint8)

        ph, pw = cfg.rows * cfg.cell_h, cfg.cols * cfg.cell_w
        self.ph, self.pw = ph, pw

        self.base = np.full((ph, pw, 3), (20, 20, 20), np.uint8)
        self.final = np.empty((ph, pw, 3), np.uint8)
        self.colors_px = np.empty((ph, pw, 3), np.uint8)
        self.masks_px = np.empty((ph, pw), np.uint8)
        self.compose = np.empty((ph, pw, 3), np.uint16)

        self._gstack_key = None
        self._gstack = None
        self._flashes: dict[tuple[int,int], list] = {}

    def add_tile_flash(self, wx: int, wy: int, color: tuple, duration: float, intensity: float = 1.0):
        ia = int(intensity * 255)
        self._flashes[(wx, wy)] = [color[0], color[1], color[2], ia, duration, duration, ia]

    def tick_flashes(self, dt: float):
        dead = []
        for k, v in list(self._flashes.items()):
            v[4] -= dt
            if v[4] <= 0:
                dead.append(k)
                continue
            ratio = max(0.0, v[4] / v[5])
            v[3] = int(v[6] * ratio)
        for k in dead:
            self._flashes.pop(k, None)

    def render(self, surface: pygame.Surface, sonar: Sonar, chunks, ecs, camera_eid: int = 0):
        cfg = self.cfg
        if not ecs.active[camera_eid]:
            return 0.0, 0.0, 0, 0

        pid = camera_eid
        px = float(ecs.pos_x[pid])
        py = float(ecs.pos_y[pid])
        cam_x = int(px) - cfg.cols // 2
        cam_y = int(py) - cfg.rows // 2
        vp_px, vp_py = px - cam_x, py - cam_y

        mat = chunks.sample_viewport(cam_x, cam_y)
        vis = sonar.mask(vp_px, vp_py)
        indices = np.minimum(mat, vis).astype(np.uint8)

        # Expand palette and glyphs
        cell_colors = self.palette[indices]
        self.colors_px[:] = np.broadcast_to(
            cell_colors[:,:,None,None,:], (cfg.rows, cfg.cols, cfg.cell_h, cfg.cell_w, 3)
        ).transpose(0,2,1,3,4).reshape(self.ph, self.pw, 3)

        self.masks_px[:] = (
            np.stack([self.atlas.get(chr(i), (255,255,255)) for i in range(256)], axis=0)[indices]
            .transpose(0,2,1,3)
            .reshape(self.ph, self.pw)
        )

        # Integer composite
        a16 = self.masks_px.astype(np.uint16)
        np.multiply(self.base.astype(np.uint16), (255 - a16)[..., None], out=self.compose)
        self.compose += self.colors_px.astype(np.uint16) * a16[..., None]
        self.compose //= 255
        self.final[:] = self.compose.astype(np.uint8)

        # Tile flashes
        for (wx, wy), v in self._flashes.items():
            vx = wx - cam_x
            vy = wy - cam_y
            if not (0 <= vx < cfg.cols and 0 <= vy < cfg.rows):
                continue
            px0, py0 = vx * cfg.cell_w, vy * cfg.cell_h
            px1, py1 = px0 + cfg.cell_w, py0 + cfg.cell_h
            fc = np.array(v[:3], np.uint16)
            fa = min(255, v[3])
            reg = self.final[py0:py1, px0:px1].astype(np.uint16)
            self.final[py0:py1, px0:px1] = ((reg * (255 - fa) + fc * fa) // 255).astype(np.uint8)

        # Entities
        for i in np.flatnonzero(ecs.active):
            ex = int(round(float(ecs.pos_x[i]))) - cam_x
            ey = int(round(float(ecs.pos_y[i]))) - cam_y
            px0, py0 = ex * cfg.cell_w, ey * cfg.cell_h
            if not (0 <= px0 < self.pw and 0 <= py0 < self.ph):
                continue
            x1 = min(self.pw, px0 + cfg.cell_w)
            y1 = min(self.ph, py0 + cfg.cell_h)
            ch = chr(int(ecs.char_ord[i]))
            mask = self.atlas.get(ch, (255,255,255)).get_alpha().astype(np.uint16)
            ec = np.array((ecs.col_r[i], ecs.col_g[i], ecs.col_b[i]), np.uint16)
            reg = self.final[py0:y1, px0:x1].astype(np.uint16)
            self.final[py0:y1, px0:x1] = ((reg * (255 - mask[..., None]) + ec * mask[..., None]) // 255).astype(np.uint8)

        # Final blit
        pygame.surfarray.blit_array(self.layer, np.ascontiguousarray(self.final.transpose(1, 0, 2)))
        surface.blit(self.layer, (0, 0))

        return cam_x, cam_y, int(vp_px), int(vp_py)