from simulation import Simulation
import engine
import pygame as pg
import configuration as c
import math
renderer = engine.renderer

def get_rotated_rect(rect: pg.Rect, angle: float, center_pos: pg.Vector2) -> list[pg.Vector2]:
    cx, cy = center_pos
    rad = math.radians(angle)

    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    
    corners = [
        (-rect.w / 2, -rect.h / 2),  # top-left
        ( rect.w / 2, -rect.h / 2),  # top-right
        ( rect.w / 2,  rect.h / 2),  # bottom-right
        (-rect.w / 2,  rect.h / 2),  # bottom-left
    ]

    rotated_points: list[pg.Vector2] = []
    
    for x, y in corners:
        # 2D rotation
        rx = x * cos_a - y * sin_a
        ry = x * sin_a + y * cos_a
        rotated_points.append(pg.Vector2(cx + rx, cy + ry))
    
    return rotated_points

def render_sim(simulation: Simulation):
    rocket = simulation.rocket
    # renderer.draw_circle((30, 30), 25, (255, 255, 255), camera_offset=True)
    
    renderer.draw_line((c.DISPLAY.WIDTH_CENTER, c.DISPLAY.HEIGHT_CENTER - 10), (c.DISPLAY.WIDTH_CENTER, c.DISPLAY.HEIGHT_CENTER + 10), (255, 255, 255), 2)
    renderer.draw_line((c.DISPLAY.WIDTH_CENTER - 10, c.DISPLAY.HEIGHT_CENTER), (c.DISPLAY.WIDTH_CENTER + 10, c.DISPLAY.HEIGHT_CENTER), (255, 255, 255), 2)
    
    # draw ground
    renderer.draw_rect(pg.Rect(-engine.camera.get_offset().x, 0, c.DISPLAY.WIDTH, 20), (80, 80, 80), camera_offset=True)
    
    renderer.draw_polygon(get_rotated_rect(pg.Rect(rocket.pos, (20, rocket.length)), rocket.rot, rocket.pos), (255, 255, 255), camera_offset = True)