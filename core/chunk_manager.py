import numpy as np
import collections
from dataclasses import dataclass

@dataclass
class _Chunk:
    cx: int
    cy: int
    data: np.ndarray
    active: bool = True
    sleep_frames: int = 0
    changed: bool = False

def _chunk_seed(cx: int, cy: int) -> int:
    return hash((cx, cy)) & 0xFFFFFFFF

class ChunkManager:
    def __init__(self, cfg):
        self.cfg = cfg
        self.loaded: dict[tuple[int, int], _Chunk] = {}

    def world_to_chunk(self, wx: int, wy: int):
        return wx // self.cfg.chunk_w, wy // self.cfg.chunk_h

    def update_active_set(self, pwx: float, pwy: float):
        cfg = self.cfg
        pcx, pcy = self.world_to_chunk(int(pwx), int(pwy))
        needed = set()
        for dy in range(-cfg.load_radius, cfg.load_radius + 1):
            for dx in range(-cfg.load_radius, cfg.load_radius + 1):
                key = (pcx + dx, pcy + dy)
                needed.add(key)
                if key not in self.loaded:
                    self.loaded[key] = self._gen(key[0], key[1])

        for k in list(self.loaded.keys()):
            if k not in needed:
                del self.loaded[k]

    def sample_viewport(self, cam_x: int, cam_y: int) -> np.ndarray:
        cfg = self.cfg
        world_x = np.arange(cfg.cols, dtype=np.int32) + cam_x
        world_y = np.arange(cfg.rows, dtype=np.int32) + cam_y
        chunk_col = world_x // cfg.chunk_w
        chunk_row = world_y // cfg.chunk_h
        local_col = world_x % cfg.chunk_w
        local_row = world_y % cfg.chunk_h

        out = np.zeros((cfg.rows, cfg.cols), np.uint8)
        for ccy in set(chunk_row):
            vy_mask = chunk_row == ccy
            ly = local_row[vy_mask]
            for ccx in set(chunk_col):
                ch = self.loaded.get((ccx, ccy))
                if ch is None:
                    continue
                vx_mask = chunk_col == ccx
                lx = local_col[vx_mask]
                out[np.ix_(vy_mask, vx_mask)] = ch.data[np.ix_(ly, lx)]
        return out

    def set_cell(self, wx: int, wy: int, mat: int):
        cx, cy = self.world_to_chunk(wx, wy)
        ch = self.loaded.get((cx, cy))
        if ch is not None:
            ch.data[wy % self.cfg.chunk_h, wx % self.cfg.chunk_w] = mat
            ch.active = True
            ch.sleep_frames = 0

    def _gen(self, cx: int, cy: int) -> _Chunk:
        cfg = self.cfg
        rng = np.random.default_rng(_chunk_seed(cx, cy))
        data = np.digitize(
            rng.random((cfg.chunk_h, cfg.chunk_w), dtype=np.float32),
            [0.20, 0.40, 0.60, 0.80]
        ).astype(np.uint8)
        return _Chunk(cx, cy, data)