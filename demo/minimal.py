"""
Minimal ASCIO Demo
Shows the absolute basics: player movement + one light.
"""
import pygame
import ascio

cfg = ascio.Config(
    cols=80,
    rows=50,
    cell_w=7,
    cell_h=12,
    title="Ascio — Minimal Demo",
    scale=2,
    ambient=(4, 8, 16),
)

game = ascio.Ascio(cfg)

# Spawn player
player = game.spawn(10, 10, '@', color=(255, 255, 255))

# Add a warm torch light
torch = game.add_point_light(15, 12, radius=14, intensity=0.9, color=(255, 180, 80))

def update(dt: float):
    # Simple WASD movement
    vx = vy = 0.0
    if game.key_held(pygame.K_w) or game.key_held(pygame.K_UP):    vy -= 1
    if game.key_held(pygame.K_s) or game.key_held(pygame.K_DOWN):  vy += 1
    if game.key_held(pygame.K_a) or game.key_held(pygame.K_LEFT):  vx -= 1
    if game.key_held(pygame.K_d) or game.key_held(pygame.K_RIGHT): vx += 1

    if vx or vy:
        length = (vx*vx + vy*vy) ** 0.5
        vx /= length
        vy /= length

    game.set_velocity(player, vx * 22, vy * 22)

print("Minimal Demo Controls:")
print("   WASD / Arrows = Move")
print("   ESC = Quit")
game.run(update)