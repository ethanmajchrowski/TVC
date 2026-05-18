import pygame as pg
from typing import Callable
import engine
import configuration as c

class DebugRenderer:
    def __init__(self) -> None:
        self.data_fields = []
        
        self.font = pg.font.Font(r"assets\font\inter24.ttf")
        
    def add_field(self, name: str, getter: Callable):
        self.data_fields.append((name, getter))
    
    def render(self):
        if not c.DEBUG_MODE: return
        for i, val in enumerate(self.data_fields):
            name, getter = val
            f = self.font.render(f"{name}: {getter()}", True, (255, 255, 255))
            engine.renderer.draw_sprite(f, (10, 10 + i*f.height))