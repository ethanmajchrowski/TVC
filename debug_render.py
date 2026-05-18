from typing import Callable
import engine
import configuration as c

class DebugRenderer:
    def __init__(self) -> None:
        self.data_fields = []
        
    def add_field(self, name: str, getter: Callable):
        self.data_fields.append((name, getter))
    
    def add_spacer(self, label: str = ""):
        self.data_fields.append(label)
    
    def render(self):
        if not c.DEBUG_MODE: return
        for i, val in enumerate(self.data_fields):
            offset = 0
            if isinstance(val, str):
                text = val
                offset = 50
            else:
                name, getter = val
                text = f"{name}: {getter()}"
            
            f = c.font.render(text, True, (255, 255, 255))
            engine.renderer.draw_sprite(f, (10 + offset, 10 + i*f.height))