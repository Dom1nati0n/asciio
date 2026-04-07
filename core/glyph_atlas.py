from functools import lru_cache
import pygame

class GlyphAtlas:
    def __init__(self, cell_w=7, cell_h=12):
        self.font = pygame.font.SysFont('Courier New', 14, bold=True)
        self.cell_w = cell_w
        self.cell_h = cell_h
        self.cache = {}

    @lru_cache(maxsize=2048)
    def get(self, ch: str, color: tuple) -> pygame.Surface:
        qc = tuple(c // 8 * 8 for c in color)
        surf = self.font.render(ch, False, (255,255,255)).convert_alpha()
        cell = pygame.Surface((self.cell_w, self.cell_h), pygame.SRCALPHA)
        cell.blit(surf, surf.get_rect(center=(self.cell_w//2, self.cell_h//2)))
        cell.fill(qc, special_flags=pygame.BLEND_RGB_MULT)
        return cell