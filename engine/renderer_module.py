from logger import logger
import pygame as pg
from pygame.math import Vector2
from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from engine.camera_ import Camera
import configuration as c
import math

class RendererAPI:
    def __init__(self) -> None:
        self.queue = []
        self.camera: "Camera"
        self.screen: Any
        self.fill_color = (0, 0, 0)
    
    def setup(self, camera: "Camera", screen):
        self.screen = screen
        self.camera = camera

    def begin_frame(self): pass
    def end_frame(self): pass

    def set_fill_color(self, color): 
        self.fill_color = color
    
    def draw_sprite(self, texture, position: tuple | pg.Rect | pg.Vector2, rotation=0.0, scale=1, layer=0, camera_offset: bool = False, anchor="topleft"): pass
    
    def draw_line(self, start, end, color, width=1, layer=0, camera_offset: bool = False): pass
    
    def draw_circle(self, position, radius, color, width=0, layer=0, camera_offset: bool = False): pass
    
    def draw_rect(self, rect, color, width=0, layer=0, border_radius=0, camera_offset: bool = False): pass
    
    def render(self): pass

class _PygameRenderer(RendererAPI):
    def __init__(self) -> None:
        super().__init__()

    def setup(self, camera: "Camera", screen):
        self.screen = screen
        self.camera = camera
        
    def begin_frame(self):
        self.screen.fill(self.fill_color)
    
    def end_frame(self):
        pass
    
    def set_fill_color(self, color):
        self.fill_color = color
    
    def draw_sprite(self, texture, position: tuple | pg.Rect | pg.Vector2, rotation=0.0, scale=1, layer=0, camera_offset: bool = False, anchor="topleft"):
        if isinstance(position, pg.Rect): position = position.topleft
        if isinstance(position, pg.Vector2): position = tuple(position)

        if rotation:
            texture = pg.transform.rotate(texture, rotation)

        match anchor:
            case "topleft":
                position = position
            case "center":
                position = (position[0] - texture.width//2, position[1] - texture.height//2)
        
            
        
        self.queue.append({"type": "sprite", "texture": texture, "pos": position, "rotation": rotation, "scale": scale, "layer": layer, "camera_offset": camera_offset})
    
    def draw_line(self, start, end, color, width=1, layer=0, camera_offset: bool = False):
        self.queue.append({"type": "line", "start": start, "end": end, "color": color, "width": width, "layer": layer, "camera_offset": camera_offset})
    
    def draw_circle(self, position, radius, color, width=0, layer=0, camera_offset: bool = False):
        self.queue.append({"type": "circle", "pos": position, "radius": radius, "color": color, "width": width, "layer": layer, "camera_offset": camera_offset})
    
    def draw_rect(self, rect, color, width=0, layer=0, border_radius=0, camera_offset: bool = False):
        self.queue.append({"type": "rect", "rect": rect, "color": color, "width": width, "layer": layer, "border_radius": border_radius, "camera_offset": camera_offset})
    
    def draw_polygon(self, points: list[pg.Vector2], color, width=0, layer=0, camera_offset: bool = False):
        self.queue.append({"type": "polygon", "points": points, "color": color, "width": width, "layer": layer, "camera_offset": camera_offset})
    
    def render(self):
        # sort queue by layer
        sorted_queue = sorted(self.queue, key = lambda item: item["layer"])
        self.queue.clear()
        camera_offset = self.camera.get_offset()
        
        while sorted_queue:
            item = sorted_queue.pop(0)
            match item["type"]:
                case "sprite":
                    # camera offsets
                    pos = item["pos"] + camera_offset if item["camera_offset"] else item["pos"]
                    self.screen.blit(item["texture"], pos)
                case "line":
                    # camera offsets
                    start = item["start"] + camera_offset if item["camera_offset"] else item["start"]
                    end = item["end"] + camera_offset if item["camera_offset"] else item["end"]
                    
                    pg.draw.aaline(self.screen, item["color"], start, end, item["width"])
                case "circle":
                    # camera offsets
                    pos = item["pos"] + camera_offset if item["camera_offset"] else item["pos"]

                    pg.draw.aacircle(self.screen, item["color"], pos, item["radius"], item["width"])
                case "rect":
                    # make sure it is a pygame rect
                    if not isinstance(item["rect"], pg.Rect):
                        item["rect"] = pg.rect.Rect(item["rect"])
                    
                    # camera offsets
                    rect = item["rect"].move(camera_offset) if item["camera_offset"] else item["rect"]
                    
                    pg.draw.rect(self.screen, item["color"], rect, item["width"], item["border_radius"])
                
                case "polygon":
                    if not item["camera_offset"]: 
                        pg.draw.polygon(self.screen, item["color"], item["points"], item["width"])
                        continue
                        
                    pg.draw.polygon(self.screen, item["color"], [point + camera_offset for point in item["points"]], item["width"])


    def draw_grid(self, surface, tile_size):
        """
        Draws an infinite scrolling grid using camera offsets.

        camera_x, camera_y:
            Position of the camera in world coordinates.
        """

        width, height = surface.get_size()

        # Offset inside the current tile
        camera_x, camera_y = self.camera.get_offset()
        offset_x = camera_x % tile_size
        offset_y = camera_y % tile_size

        # Number of lines needed to fully cover screen
        cols = math.ceil(width / tile_size) + 2
        rows = math.ceil(height / tile_size) + 2

        # Vertical lines
        for col in range(cols):
            x = col * tile_size + offset_x
            pg.draw.line(surface, c.GRID_COLOR, (x, 0), (x, height))

        # Horizontal lines
        for row in range(rows):
            y = row * tile_size + offset_y
            pg.draw.line(surface, c.GRID_COLOR, (0, y), (width, y))

