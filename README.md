Markdown# ASCIO — CPU-Only ASCII Renderer & World Engine

**The last ASCII/roguelike rendering engine you'll ever need.**

A fast, clean, production-grade **CPU-only** (no GPU) renderer for terminal-style and roguelike games. Built from years of iteration to deliver beautiful lighting, smooth chunk streaming, and a delightful developer experience.

![Ascio Deep Trench Demo](https://via.placeholder.com/800x400/0a1422/00ddff?text=Ascio+Deep+Trench)  
*(Replace with a real screenshot once you have one)*

## Features

- **Pure CPU + NumPy** — Runs beautifully even on low-end machines
- **Fixed 7×12 cell size** — The sweet spot for crisp monospace ASCII
- **Advanced dynamic lighting** — Radial + area lights with world-anchored Bayer-4 dithering
- **Chunked infinite world** — Streaming + gravity simulation + sleep optimization
- **Clean public API** — Focus on your game logic, not rendering
- **Integer-heavy render pipeline** — No float32 crashes in Pygame
- **Glyph atlas with color quantization** — Excellent performance + cache hits
- **Optional rich world extension** — Biomes, rivers, villages, caverns, day/night cycle

## Quick Start

```bash
pip install pygame numpy
Pythonimport pygame
import ascio

cfg = ascio.Config(
    cols=120,
    rows=70,
    title="My ASCII Game",
    scale=2,
    ambient=(2, 4, 10)
)

game = ascio.Ascio(cfg)

# Spawn player
player = game.spawn(10, 10, '@', color=(255, 255, 255))

# Add a warm torch
torch = game.add_point_light(15, 12, radius=14, intensity=0.9, color=(255, 180, 80))

def update(dt: float):
    # Simple movement
    vx = vy = 0.0
    if game.key_held(pygame.K_w) or game.key_held(pygame.K_UP):    vy -= 1
    if game.key_held(pygame.K_s) or game.key_held(pygame.K_DOWN):  vy += 1
    if game.key_held(pygame.K_a) or game.key_held(pygame.K_LEFT):  vx -= 1
    if game.key_held(pygame.K_d) or game.key_held(pygame.K_RIGHT): vx += 1

    if vx or vy:
        length = (vx*vx + vy*vy)**0.5
        game.set_velocity(player, vx/length*22, vy/length*22)

game.run(update)
Demos
Bash# Minimal demo (just renderer + movement)
python -m ascio.demo.minimal

# Full atmospheric demo (sonar waves, multiple lights, projectiles)
python -m ascio.demo.deep_trench
Project Structure
textascio/
├── ascio.py                 # Main public class
├── config.py
├── core/                    # Core rendering engine
│   ├── ecs.py
│   ├── chunk_manager.py
│   ├── glyph_atlas.py
│   ├── light_system.py      # Best-in-class colored lighting
│   ├── renderer.py
│   └── sonar.py
├── world/                   # Optional rich world simulation
│   ├── biome.py
│   └── terrain_generator.py
└── demo/
    ├── minimal.py
    └── deep_trench.py
Why ASCIO?
After many iterations across different prototypes, ASCIO combines:

The clean renderer from ascio.py
The best lighting system from the world engines
The rock-solid chunk streaming and simulation
Integer-only compositing to avoid Pygame C-API issues
World-anchored Bayer dithering for beautiful soft lighting edges

It is designed to feel like a modern NetHack or Dwarf Fortress renderer while remaining extremely lightweight and CPU-only.
Future Plans

Full rich world extension (rivers, villages, caverns, day/night)
Save/load system
More built-in demos
Optional shader path for users who want GPU acceleration

License
MIT License — feel free to use it in your games.
Contributing
Pull requests welcome! Especially for:

More lighting effects
Additional world generation features
Performance improvements


Made with love for the ASCII/roguelike community.
