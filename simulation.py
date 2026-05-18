from pygame.math import Vector2

class Rocket:
    def __init__(self) -> None:
        self.pos = Vector2()
        self.vel = Vector2()
        self.accel = Vector2()
        
        self.length = 80
        
        self.rot = 0.0
        
        self.engine_angle = 0.0
        self.thrust_force = 300 # newtons

class Simulation:
    def __init__(self) -> None:
        self.paused: bool = False
        self.rocket = Rocket()

    def tick(self, dt: float) -> None:
        if self.paused: return
        self.rocket.accel = Vector2()
        
        # self.rocket.rot += dt * 90
        
        self.rocket.accel.y += -98.1
        
        # compute thrust vector
        thrust = Vector2(0.0, self.rocket.thrust_force)
        thrust.rotate_ip(self.rocket.rot)

        self.rocket.accel += thrust
        
        # apply acceleration
        self.rocket.vel -= self.rocket.accel * dt
        self.rocket.pos += self.rocket.vel * dt