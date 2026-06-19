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
    
    renderer.draw_line((-c.DISPLAY.WIDTH, -rocket.max_height), (c.DISPLAY.WIDTH, -rocket.max_height), (0, 100, 0), camera_offset=True)
    
    rocket_bottom = rocket.pos + pg.Vector2(0, rocket.length_cm // 2).rotate(rocket.rot_deg)
    # renderer.draw_circle((30, 30), 25, (255, 255, 255), camera_offset=True)
    # draw rocket body
    rocket_width = 20
    renderer.draw_polygon(get_rotated_rect(pg.Rect(rocket.pos, (rocket_width, rocket.length_cm)), rocket.rot_deg, rocket.pos), (80, 120, 80), camera_offset = True)

    # draw camera cross
    renderer.draw_line((c.DISPLAY.WIDTH_CENTER, c.DISPLAY.HEIGHT_CENTER - 10), (c.DISPLAY.WIDTH_CENTER, c.DISPLAY.HEIGHT_CENTER + 10), (255, 255, 255), 2)
    renderer.draw_line((c.DISPLAY.WIDTH_CENTER - 10, c.DISPLAY.HEIGHT_CENTER), (c.DISPLAY.WIDTH_CENTER + 10, c.DISPLAY.HEIGHT_CENTER), (255, 255, 255), 2)
    
    # draw ground
    renderer.draw_rect(pg.Rect(-engine.camera.get_offset().x, 0, c.DISPLAY.WIDTH, 20), (80, 80, 80), camera_offset=True)
    
    renderer.draw_circle(rocket_bottom, 5, (255, 0, 255), camera_offset=True)

    # draw engine direction line
    renderer.draw_line(rocket_bottom, rocket_bottom + pg.Vector2(0, 50).rotate(rocket.rot_deg + rocket.engine_angle), (255, 0, 255), 3, camera_offset=True)
    renderer.draw_line(rocket_bottom, (rocket_bottom.x, rocket_bottom.y + pg.Vector2(0, 50).rotate(rocket.rot_deg + rocket.engine_angle).y), (255, 0, 0), 3, camera_offset=True)
    renderer.draw_line(rocket_bottom, (rocket_bottom.x + pg.Vector2(0, 50).rotate(rocket.rot_deg + rocket.engine_angle).x, rocket_bottom.y), (0, 0, 255), 3, camera_offset=True)

    if simulation.paused:
        f = c.font.render("PAUSED", True, (100, 100, 255), (0, 0, 0))
        fr = f.get_rect(center=(c.DISPLAY.WIDTH_CENTER, 10 + f.height//2))
        renderer.draw_sprite(f, fr)