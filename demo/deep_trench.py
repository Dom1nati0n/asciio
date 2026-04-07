"""
Deep Trench Demo — Full atmospheric showcase
Bioluminescent sonar waves, multiple colored lights, projectiles, flashes
"""
import math
import random
import pygame
import ascio

cfg = ascio.Config(
    cols=120,
    rows=70,
    cell_w=7,
    cell_h=12,
    title="Ascio — Deep Trench",
    scale=1,
    ambient=(2, 4, 10),
)

game = ascio.Ascio(cfg)

# Player submarine
player = game.spawn(15, 20, '@', color=(255, 255, 255))

# Static environmental lights
game.add_point_light(30, 25, radius=22, intensity=0.85, color=(0, 180, 255))      # blue vent
game.add_area_light(70, 45, width=20, height=8, intensity=0.75,
                    color=(255, 80, 30), edge_falloff=5.0)                       # orange trench glow

# Pulsing alien crystal node
node_light = game.add_point_light(95, 18, radius=13, intensity=0.65, color=(160, 40, 255))
node_pulse = 0.0

fire_cd = 0.0
flash_cd = 0.0

def update(dt: float):
    global fire_cd, flash_cd, node_pulse

    # ── Movement ─────────────────────────────────────
    dx = dy = 0.0
    if game.key_held(pygame.K_w) or game.key_held(pygame.K_UP):    dy -= 1
    if game.key_held(pygame.K_s) or game.key_held(pygame.K_DOWN):  dy += 1
    if game.key_held(pygame.K_a) or game.key_held(pygame.K_LEFT):  dx -= 1
    if game.key_held(pygame.K_d) or game.key_held(pygame.K_RIGHT): dx += 1

    if dx or dy:
        n = (dx*dx + dy*dy) ** 0.5
        dx /= n
        dy /= n
    game.set_velocity(player, dx * 24.0, dy * 24.0)

    px, py = game.get_pos(player)

    # ── Shoot projectile ─────────────────────────────
    fire_cd -= dt
    if game.key_held(pygame.K_SPACE) and fire_cd <= 0:
        fire_cd = 0.16
        angle = node_pulse * 4.0
        vx = math.cos(angle) * 48
        vy = math.sin(angle) * 48
        game.spawn_projectile(px, py, '·', (80, 220, 255), vx, vy, lifetime=1.3)
        game.flash_tile(int(px), int(py), color=(180, 255, 255), duration=0.1)

    # ── Sonar ping (F) ───────────────────────────────
    flash_cd -= dt
    if game.key_held(pygame.K_f) and flash_cd <= 0:
        flash_cd = 0.35
        for ox in range(-2, 3):
            for oy in range(-2, 3):
                game.flash_tile(int(px)+ox, int(py)+oy,
                                color=(0, 230, 180), duration=0.55, intensity=0.75)

    # ── Screen flash (E) ─────────────────────────────
    if game.key_held(pygame.K_e):
        game.screen_flash(color=(60, 0, 140), intensity=0.75)

    # ── Pulsing node ─────────────────────────────────
    node_pulse += dt
    node_light.intensity = 0.45 + 0.38 * math.sin(node_pulse * 2.8)

    # ── Random bioluminescent spores ─────────────────
    if random.random() < 0.035:
        sx = int(px) + random.randint(-28, 28)
        sy = int(py) + random.randint(-18, 18)
        game.flash_tile(sx, sy, color=(0, 255, 170), duration=0.65, intensity=0.7)
        game.add_point_light(sx, sy, radius=5, intensity=0.55,
                             color=(40, 255, 200), lifetime=0.6)


print("="*60)
print("DEEP TRENCH DEMO")
print("WASD/Arrows = Move")
print("SPACE       = Shoot")
print("F           = Sonar Ping")
print("E           = Screen Flash")
print("ESC         = Quit")
print("="*60)

game.run(update)