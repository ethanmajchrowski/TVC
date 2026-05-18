from pygame.math import Vector2

class Rocket:
    def __init__(self) -> None:
        self.pos = Vector2()
        self.vel = Vector2()
        self.accel = Vector2()
        
        self.angular_accel = 0.0
        self.angular_vel = 0.0
        self.rot = 0.0
        
        self.length = 80
        self.mass = 2.0
        
        self.engine_angle = 0.0
        self.thrust_force = 100 # newtons
        self.moment_inertia = 5

class Simulation:
    def __init__(self) -> None:
        self.paused: bool = False
        self.rocket = Rocket()

    def tick(self, dt: float) -> None:
        if self.paused: return
        self.rocket.accel = Vector2()
        self.rocket.angular_accel = 0.0
        
        # self.rocket.rot += dt * 90
        
        # self.rocket.accel.y += -98.1
        
        # compute thrust vector
        thrust = Vector2(0.0, self.rocket.thrust_force)
        thrust.rotate_ip(self.rocket.rot + self.rocket.engine_angle)

        self.rocket.accel += thrust / self.rocket.mass # F = ma, a = F / m
        
        torque = Vector2(0, self.rocket.thrust_force).rotate(self.rocket.rot + self.rocket.engine_angle).x * self.rocket.length / 2
        self.rocket.angular_accel += torque / self.rocket.moment_inertia
        
        # apply angular accel
        self.rocket.angular_vel += self.rocket.angular_accel * dt
        self.rocket.rot += self.rocket.angular_vel * dt
        
        # apply acceleration
        self.rocket.vel -= self.rocket.accel * dt
        self.rocket.pos += self.rocket.vel * dt