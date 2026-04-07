from dataclasses import dataclass
from typing import Tuple

Color = Tuple[int, int, int]

# Biome IDs
BIOME_OCEAN = 0
BIOME_SHALLOW = 1
BIOME_BEACH = 2
BIOME_DESERT = 3
BIOME_SAVANNA = 4
BIOME_SCRUB = 5
BIOME_PLAINS = 6
BIOME_TEMP_FOREST = 7
BIOME_SWAMP = 8
BIOME_TROP_FOREST = 9
BIOME_TAIGA = 10
BIOME_TUNDRA = 11
BIOME_MOUNTAIN = 12
BIOME_SNOW = 13

@dataclass(frozen=True)
class Biome:
    id: int
    name: str
    glyph: str
    fg: Color
    bg: Color
    flora_glyphs: tuple = ()
    flora_color: Color | None = None
    flora_density: float = 0.0
    fauna: tuple = ()           # list of (glyph, color) tuples
    can_village: bool = False

BIOMES = [
    Biome(0, "Ocean",      '~', (40,  90, 150), (10, 20,  50), fauna=(('f', (70,150,195)),)),
    Biome(1, "Shallows",   '=', (80, 160, 200), (20, 50,  90)),
    Biome(2, "Beach",      '.', (210,190,120), (80, 70,  30)),
    Biome(3, "Desert",     '.', (220,190, 80), (100,80,  30), ('o','Y','.'), (195,165,60), 0.07,
          (('s',(195,170,90)), ('e',(160,140,55)))),
    Biome(4, "Savanna",    '"', (160,180, 60), (55, 50,  18), ('"','Y','T'), (140,158,48), 0.12,
          (('z',(210,185,90)), ('l',(195,150,70))), True),
    Biome(5, "Scrubland",  ':', (130,140, 70), (42, 38,  14), (':',';','o'), (110,120,58), 0.08),
    Biome(6, "Plains",     '"', (120,200, 90), (25, 50,  25), ('"',';',':'), (62,138,50), 0.10,
          (('d',(180,160,120)), ('r',(200,170,140))), True),
    Biome(7, "Forest",     '"', (80, 160, 70), (20, 40,  20), ('T','Y','&'), (52,130,42), 0.35,
          (('d',(165,145,110)), ('b',(100,80,60))), True),
    Biome(8, "Swamp",      '%', (100,130, 80), (25, 35,  20), ('%','&','o'), (82,112,62), 0.25,
          (('f',(80,130,80)), ('c',(55,115,50)))),
    Biome(9, "Jungle",     '"', (40, 140, 60), (10, 35,  15), ('T','&','Y'), (30,120,48), 0.45,
          (('m',(80,175,80)), ('p',(170,55,55))), True),
    Biome(10,"Taiga",      '"', (70, 120, 90), (15, 30,  20), ('T','Y','^'), (60,88,70), 0.30,
          (('w',(200,200,200)), ('b',(100,80,60))), True),
    Biome(11,"Tundra",     '.', (180,190,170), (60, 65,  60), ('.','o','.'), (152,160,150), 0.05,
          (('w',(230,230,240)), ('o',(195,195,190)))),
    Biome(12,"Mountains",  '^', (150,150,150), (40, 40,  40), (), None, 0.0,
          (('e',(175,175,180)),)),
    Biome(13,"Snowpeaks",  '^', (255,255,255), (140,140,160), (), None, 0.0,
          (('e',(175,175,180)),)),
]

BIOME_MAP = {b.id: b for b in BIOMES}
LAND_BIOMES = {b.id for b in BIOMES if b.id >= 2}