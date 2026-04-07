import numpy as np
import collections

_MAX_ENTITIES = 1000

class ECS:
    def __init__(self):
        n = _MAX_ENTITIES
        self.active    = np.zeros(n, np.bool_)
        self.pos_x     = np.zeros(n, np.float32)
        self.pos_y     = np.zeros(n, np.float32)
        self.vel_x     = np.zeros(n, np.float32)
        self.vel_y     = np.zeros(n, np.float32)
        self.char_ord  = np.zeros(n, np.int32)
        self.col_r     = np.zeros(n, np.uint8)
        self.col_g     = np.zeros(n, np.uint8)
        self.col_b     = np.zeros(n, np.uint8)
        self.lifetime  = np.full(n, -1.0, np.float32)
        self._free     = collections.deque(range(n))

    def create(self) -> int:
        if not self._free:
            raise RuntimeError("Entity pool exhausted")
        eid = self._free.popleft()
        self.active[eid] = True
        self.lifetime[eid] = -1.0
        return eid

    def destroy(self, eid: int) -> None:
        self.active[eid] = False
        self._free.append(eid)

    def tick_lifetimes(self, dt: float) -> None:
        mask = self.active & (self.lifetime > 0)
        if not np.any(mask):
            return
        self.lifetime[mask] -= dt
        for eid in np.flatnonzero(self.lifetime <= 0):
            self.destroy(int(eid))