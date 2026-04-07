from dataclasses import dataclass

@dataclass
class Config:
    cols:         int   = 120
    rows:         int   = 70
    cell_w:       int   = 7
    cell_h:       int   = 12
    title:        str   = "Ascio"
    scale:        int   = 2
    target_fps:   int   = 0
    fixed_dt:     float = 1.0 / 60.0
    ambient:      tuple = (2, 4, 8)
    falloff_exp:  float = 1.7
    dither_scale: float = 0.065

    # Chunk system
    chunk_w:      int = 64
    chunk_h:      int = 64
    load_radius:  int = 18
    sim_radius:   int = 16

    @property
    def internal_w(self) -> int: return self.cols * self.cell_w
    @property
    def internal_h(self) -> int: return self.rows * self.cell_h