import pygame as pg

class _DISPLAY:
    def __init__(self) -> None:
        self.update_window_size((1920, 1080))
    
    def update_window_size(self, window_size: tuple):
        w, h = window_size
        
        self.WIDTH = w
        self.HEIGHT = h

        self.SIZE = (self.WIDTH, self.HEIGHT)
        self.WIDTH_CENTER = self.WIDTH // 2
        self.HEIGHT_CENTER = self.HEIGHT // 2
        self.CENTER = (self.WIDTH_CENTER, self.HEIGHT_CENTER)

DISPLAY = _DISPLAY()

DEBUG_MODE = True

WINDOW_TITLE = "TVC 2D Simulation"
# Background grid
GRID_TILE_SIZE = 512
GRID_COLOR = (70, 70, 70)

font: pg.Font