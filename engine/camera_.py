import pygame as pg
import random
import configuration as c

class Camera:
    def __init__(self, position=(0, 0), zoom=1.0):
        self.target_position = list(position)
        self.position = list(position)
        self.zoom = zoom
        
        self.smoothing: float = 0.0 # lower --> more smooth
    
        self.shake_time = 0.0
        self.shake_duration = 0.0
        self.shake_strength = 0.0
        self.shake = pg.Vector2()
    
        # self.min_zoom = 0.25
        # self.max_zoom = 4.0
    
    def set_screen_size(self):
        self.screen_width, self.screen_height = pg.display.get_window_size()

    def move(self, dx, dy, *, snap: bool = False, flip: bool = False):
        mod = -1 if flip else 1
        
        self.target_position[0] += dx * mod / self.zoom
        self.target_position[1] += dy * mod / self.zoom
        if snap or not self.smoothing:
            self.snap_pos()
    
    def get_offset(self):
        return pg.Vector2(-self.position[0] + self.shake.x, -self.position[1] + self.shake.y)

    def set_pos(self, x, y, *, snap: bool = False):
        self.target_position = [x, y]
        if snap or not self.smoothing: self.snap_pos()
    
    def center_camera(self, x, y, *, snap: bool = False):
        """Centers the camera on a x y coordinate.

        Args:
            snap (bool, optional): If true, the camera will ignore smoothing to get to the position. Defaults to False.
        """
        self.target_position = [x - c.DISPLAY.WIDTH_CENTER, y - c.DISPLAY.HEIGHT_CENTER]
        
        if snap or not self.smoothing: self.snap_pos()
    
    def snap_pos(self):
        self.position = self.target_position.copy()
        

    def world_to_screen(self, world_pos):
        return (
            (world_pos[0] - self.position[0]) * self.zoom,
            (world_pos[1] - self.position[1]) * self.zoom
        )

    def screen_to_world(self, screen_pos):
        return (
            screen_pos[0] / self.zoom + self.position[0],
            screen_pos[1] / self.zoom + self.position[1]
        )
    
    def add_shake(self, strength, duration):
        self.shake_strength = max(self.shake_strength, strength)
        self.shake_duration = duration
        self.shake_time = duration

    
    def update(self, dt):
        if self.smoothing <= 0:
            return

        dx = self.target_position[0] - self.position[0]
        dy = self.target_position[1] - self.position[1]

        # Map smoothing [0,1] to decay rate
        if self.smoothing >= 1:
            alpha = 1.0
        else:
            alpha = 1.0 - (1.0 - self.smoothing) ** dt

        self.position[0] += dx * alpha
        self.position[1] += dy * alpha
        
        self.shake.x = 0.0
        self.shake.y = 0.0

        if self.shake_time > 0:
            t = self.shake_time / self.shake_duration  # 1 → 0
            magnitude = self.shake_strength * t        # linear decay

            self.shake.x = random.uniform(-1, 1) * magnitude
            self.shake.y = random.uniform(-1, 1) * magnitude

            self.shake_time -= dt
