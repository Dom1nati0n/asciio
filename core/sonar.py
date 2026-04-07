import numpy as np

class Sonar:
    """
    Bioluminescent probability wave / sonar visibility system.
    Used to create the "walls appear only when you look at them" effect.
    """
    def __init__(self, cfg):
        self.cfg = cfg
        self.X, self.Y = np.meshgrid(np.arange(cfg.cols), np.arange(cfg.rows))
        self.t = 0.0

    def tick(self, dt: float):
        self.t += dt * 0.4

    def mask(self, vp_px: float, vp_py: float) -> np.ndarray:
        """
        Returns (ROWS, COLS) uint8 mask [0-4] representing visibility level.
        Higher values = more visible material.
        """
        wave = np.sin(self.X * 0.15 + self.t) * np.cos(self.Y * 0.15 - self.t * 0.5)
        wave += 0.5 * np.sin(self.X * 0.3 - self.t * 0.8)

        dist_sq = (self.X - vp_px) ** 2 + (self.Y - vp_py) ** 2
        mod = (wave + 1.0) * 0.5 * np.clip(1.0 - dist_sq / 500.0, 0.0, 1.0)

        return np.digitize(mod, [0.1, 0.35, 0.6, 0.85]).astype(np.uint8)