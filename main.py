import pygame as pg

import ctypes
ctypes.windll.user32.SetProcessDPIAware()

import configuration as c
from simulation import Simulation
from logger import logger
import engine
from sim_render import render_sim
from debug_render import DebugRenderer


def main():
    pg.init()
    pg.mixer.init(buffer=2048, channels=8)
    pg.font.init()
    display_surface = pg.display.set_mode(c.DISPLAY.SIZE, flags=pg.RESIZABLE)
    pg.display.set_caption(c.WINDOW_TITLE)
    c.font = pg.font.Font(r"assets\font\inter24.ttf")
    logger.info("Pygame initialized")

    engine.setup(c)
    logger.info("Engine setup")

    sim = Simulation()
    logger.info("Simulation object created")

    clock = pg.Clock()
    
    running = True
    engine.camera.set_pos(-990, -1028, snap=True)
    logger.info("Starting simulation")
    
    debug_renderer = DebugRenderer()
    debug_renderer.add_field("camera_offset", lambda: tuple(int(_) for _ in engine.camera.get_offset()))
    debug_renderer.add_spacer("Linear")
    debug_renderer.add_field("rocket_pos", lambda: tuple(int(_) for _ in sim.rocket.pos))
    debug_renderer.add_field("rocket_vel", lambda: tuple(int(_) for _ in sim.rocket.vel))
    debug_renderer.add_field("rocket_accel", lambda: tuple(int(_) for _ in sim.rocket.accel))
    debug_renderer.add_spacer("Angular")
    debug_renderer.add_field("angular_accel", lambda: int(sim.rocket.angular_accel))
    debug_renderer.add_field("angular_vel", lambda: int(sim.rocket.angular_vel))
    debug_renderer.add_field("rocket_rot", lambda: int(sim.rocket.rot))
    
    lock_camera_to_rocket: bool = True
    
    while running:
        dt = clock.tick() / 1000
        keys = pg.key.get_pressed()
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.WINDOWRESIZED:
                c.DISPLAY.update_window_size(pg.display.get_window_size())
            # other simulation controls
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    sim.paused = not sim.paused
                if event.key == pg.K_TAB:
                    lock_camera_to_rocket = not lock_camera_to_rocket
        
        
        if lock_camera_to_rocket: 
            engine.camera.center_camera(*sim.rocket.pos)
        else:
            move_vector = pg.Vector2(0.0, 0.0)
            if keys[pg.K_RIGHT]: move_vector.x = 1
            if keys[pg.K_LEFT]: move_vector.x = -1
            if keys[pg.K_DOWN]: move_vector.y = 1
            if keys[pg.K_UP]: move_vector.y = -1
            if move_vector: move_vector.normalize_ip()
            
            engine.camera.move(move_vector.x * dt * 1000, move_vector.y * dt * 1000, snap=True)
        
        if keys[pg.K_a]: rocket_turn = -90
        elif keys[pg.K_d]: rocket_turn = 90
        else: rocket_turn = 0        
        sim.rocket.rot += rocket_turn * dt

        if lock_camera_to_rocket:
            if keys[pg.K_RIGHT]: sim.rocket.engine_angle = 30
            elif keys[pg.K_LEFT]: sim.rocket.engine_angle = -30
            else: sim.rocket.engine_angle = 0
        
        sim.tick(dt)
        
        # Simulation renderer
        render_sim(sim)
        
        debug_renderer.render()
        
        # Backend rendering
        engine.renderer.begin_frame()
        engine.renderer.draw_grid(engine.renderer.screen, c.GRID_TILE_SIZE)
        engine.renderer.render()
        engine.renderer.end_frame()
        
        pg.display.flip()
    
    quit()

if __name__ == "__main__":
    main()
    