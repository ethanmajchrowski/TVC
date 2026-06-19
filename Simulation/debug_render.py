from typing import Callable
import engine
import configuration as c

class DebugRenderer:
    def __init__(self) -> None:
        self.data_fields_left = []
        self.data_fields_right = []
        
    def add_field(self, name: str, getter: Callable, right: bool = False, units: str = ""):
        if right: self.data_fields_right.append((name, getter, units))
        else: self.data_fields_left.append((name, getter, units))
    
    def add_spacer(self, label: str = "", right: bool = False):
        if right: self.data_fields_right.append(label)
        else: self.data_fields_left.append(label)
    
    def render(self):
        if not c.DEBUG_MODE: return
        for i, val in enumerate(self.data_fields_left):
            offset = 0
            if isinstance(val, str):
                text = val
                offset = 50
            else:
                name, getter, units = val
                text = f"{name}: {getter()} {units}"
            
            f = c.font.render(text, True, (255, 255, 255))
            engine.renderer.draw_sprite(f, (10 + offset, 10 + i*f.height))
        
        for i, val in enumerate(self.data_fields_right):
            offset = 0
            if isinstance(val, str):
                text = val
                offset = 50
            else:
                name, getter, units = val
                text = f"{name}: {getter()} {units}"
            
            f = c.font.render(text, True, (255, 255, 255))
            engine.renderer.draw_sprite(f, (c.DISPLAY.WIDTH - f.width - 10 - offset, 10 + i*f.height))