import pygame
from .config import Config
from .core.ecs import ECS
from .core.chunk_manager import ChunkManager
from .core.glyph_atlas import GlyphAtlas
from .core.light_system import LightSystem, PointLight
from .core.renderer import Renderer
from .core.sonar import Sonar

class Ascio:
    def __init__(self, cfg: Config = None):
        self.cfg = cfg or Config()
        pygame.init()
        pygame.font.init()

        self._window = pygame.display.set_mode(
            (self.cfg.internal_w * self.cfg.scale, self.cfg.internal_h * self.cfg.scale),
            pygame.RESIZABLE
        )
        pygame.display.set_caption(self.cfg.title)

        self._canvas = pygame.Surface((self.cfg.internal_w, self.cfg.internal_h))
        self._clock = pygame.time.Clock()

        self._ecs = ECS()
        self._chunks = ChunkManager(self.cfg)
        self._sonar = Sonar(self.cfg)
        self._atlas = GlyphAtlas(self.cfg.cell_w, self.cfg.cell_h)
        self._lights = LightSystem()
        self._renderer = Renderer(self.cfg, self._atlas, self._lights)

        self._running = False
        self._camera_eid: int | None = None
        self._keys_held = set()

    def spawn(self, x: float, y: float, char: str, color=(255,255,255)) -> int:
        eid = self._ecs.create()
        self._ecs.pos_x[eid] = x
        self._ecs.pos_y[eid] = y
        self._ecs.char_ord[eid] = ord(char[0])
        self._ecs.col_r[eid], self._ecs.col_g[eid], self._ecs.col_b[eid] = color
        if self._camera_eid is None:
            self._camera_eid = eid
        return eid

    def add_area_light(self, wx: float, wy: float, w: float, h: float, intensity: float, color=(255,220,140)):
        # Stub: treat as point light at center
        cx, cy = wx + w/2, wy + h/2
        return self.add_point_light(cx, cy, max(w, h)/2, intensity, color)

    def flash_tile(self, wx: int, wy: int, color: tuple, duration: float, intensity=1.0):
        self._renderer.add_tile_flash(wx, wy, color, duration, intensity)

    def set_velocity(self, eid: int, vx: float, vy: float):
        self._ecs.vel_x[eid] = vx
        self._ecs.vel_y[eid] = vy

    def screen_flash(self, color: tuple, duration: float, intensity=1.0):
        self._lights.screen_flash(color, duration, intensity)

    def key_held(self, key: int) -> bool:
        return key in self._keys_held

    def run(self, update=None):
        self._running = True
        accumulator = 0.0
        self._chunks.update_active_set(0, 0)

        while self._running:
            frame_time = self._clock.tick(self.cfg.target_fps) / 1000.0
            accumulator += frame_time

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self._running = False
                elif ev.type == pygame.KEYDOWN:
                    self._keys_held.add(ev.key)
                    if ev.key == pygame.K_ESCAPE:
                        self._running = False
                elif ev.type == pygame.KEYUP:
                    self._keys_held.discard(ev.key)

            while accumulator >= self.cfg.fixed_dt:
                if update:
                    update(self.cfg.fixed_dt)
                self._physics_tick(self.cfg.fixed_dt)
                accumulator -= self.cfg.fixed_dt

            self._renderer.tick_flashes(frame_time)
            self._lights.tick(frame_time)
            self._sonar.tick(frame_time)

            cam_x, cam_y, _, _ = self._renderer.render(
                self._canvas, self._sonar, self._chunks, self._ecs, self._camera_eid
            )

            # Player headlamp
            extra = []
            if self._camera_eid is not None:
                px = self._ecs.pos_x[self._camera_eid]
                py = self._ecs.pos_y[self._camera_eid]
                extra.append(PointLight(px, py, 18.0, 1.0 + 0.15 * np.sin(self._sonar.t * 12), (120, 255, 180)))

            self._lights.apply(self._canvas, extra, cam_x, cam_y)
            self._scale_to_window()

        pygame.quit()

    def _physics_tick(self, dt: float):
        mask = self._ecs.active
        self._ecs.pos_x[mask] += self._ecs.vel_x[mask] * dt
        self._ecs.pos_y[mask] += self._ecs.vel_y[mask] * dt
        self._ecs.tick_lifetimes(dt)

        if self._camera_eid is not None and self._ecs.active[self._camera_eid]:
            self._chunks.update_active_set(
                self._ecs.pos_x[self._camera_eid],
                self._ecs.pos_y[self._camera_eid]
            )

    def _scale_to_window(self):
        ww, wh = self._window.get_size()
        s = min(ww / self.cfg.internal_w, wh / self.cfg.internal_h)
        nw, nh = int(self.cfg.internal_w * s), int(self.cfg.internal_h * s)
        self._window.fill((0,0,0))
        self._window.blit(pygame.transform.scale(self._canvas, (nw, nh)),
                          ((ww - nw) // 2, (wh - nh) // 2))
        pygame.display.flip()