from pygame.math import Vector2
import hjson

class Rocket:
    def __init__(self, cfg: dict) -> None:
        """
        # Mass Properties
        TVC Mount - 80g
        Body Tube (full 5ish feet) - 836.31 g (half -> 418.2 g)
        # cardboard body -> 110g at 7in
        # fiberglass body -> 81g at 7in, 139g at 12in
        Electronics (estimate): 10g
        Battery: 10g
        Nosecone: (estimate) 90g
        
        # D motor max lift weight: 283g
        # E motor max lift weight: 397g
        """
        
        self.pos = Vector2(*cfg["rocket"]["position_m"].values()) # m
        self.vel = Vector2(*cfg["rocket"]["velocity_mps"].values()) # m/s, x y
        self.accel = Vector2() # m/s^2, x y
        
        self.angular_accel = 0.0 # deg / s^2
        self.angular_vel: float = cfg["rocket"]["angular_velocity_dps"] # deg / s
        self.rot_deg: float = cfg["rocket"]["rotation_deg"] # deg
        
        self.length_cm: float = cfg["rocket"]["length_cm"] # cm
        self.mass_kg: float = cfg["rocket"]["mass_kg"] # kilograms
        
        self.engine_target_angle: float = cfg["tvc"]["target_angle_deg"] # deg
        self.engine_angle: float = cfg["tvc"]["initial_angle_deg"] # deg
        self.engine_angle_rate: float = cfg["tvc"]["servo_rate_deg_per_sec"] # deg per second
        self.max_angle_deg: float = cfg["tvc"]["max_angle_deg"]
        
        self.thrust_force_n: float = 0 # newtons
        self.moment_inertia: float = cfg["rocket"]["moment_inertia_kgm2"] # kg * m^2
    
        with open(cfg["motor"]["thrust_curve"], 'r') as f:
            data = f.read()

            self.thrust_curve = [
                tuple(map(float, line.split(',')))
                for line in data.strip().splitlines()[1:]
            ]
            assert len(self.thrust_curve[0]) == 2
        
        self.thrust_index = 0
        
        self.max_height = 0.0

class Simulation:
    def __init__(self, config: str) -> None:
        with open(config, 'r') as f:
            cfg = hjson.load(f)
        
        self.paused: bool = cfg["simulation"]["start_paused"]
        self.pause_on_next_tick = 0
        self.rocket = Rocket(cfg)
        self.ticks = 0
        
        self.gravity = Vector2(0.0, cfg["simulation"]["gravity_mps2"])
        
        self.time: float = 0.0
        
        self.override_rocket_thrust: bool = cfg["motor"]["override_thrust_curve"]
        self.speed: float = cfg["simulation"]["speed"]

    def update_rocket_thrust(self):
        # update rocket thrust based off thrust curve
        # interpolate based on time
        if self.rocket.thrust_index == len(self.rocket.thrust_curve) - 1:
            self.rocket.thrust_force_n = 0
            return
        
        if self.time > self.rocket.thrust_curve[self.rocket.thrust_index + 1][0]: 
            self.rocket.thrust_index += 1
            if self.rocket.thrust_index == len(self.rocket.thrust_curve) - 1:
                return
            
        t1 = self.rocket.thrust_curve[self.rocket.thrust_index][0]
        t2 = self.rocket.thrust_curve[self.rocket.thrust_index + 1][0]
        lerp_factor = (self.time - t1) / (t2 - t1)
        
        t1 = self.rocket.thrust_curve[self.rocket.thrust_index][1]
        t2 = self.rocket.thrust_curve[self.rocket.thrust_index + 1][1]
        
        self.rocket.thrust_force_n = t1 + (t2 - t1) * lerp_factor
    
    def tick(self, dt: float) -> None:
        if self.paused or self.rocket.pos.y >= 0: return
        dt *= self.speed

        self.time += dt
        self.ticks += 1
        self.rocket.accel = Vector2()
        self.rocket.angular_accel = 0.0
        
        if self.override_rocket_thrust: self.rocket.thrust_force_n = 100.0
        else: self.update_rocket_thrust()
        
        if self.rocket.engine_angle < self.rocket.engine_target_angle:
            self.rocket.engine_angle += self.rocket.engine_angle_rate * dt
        elif self.rocket.engine_angle > self.rocket.engine_target_angle:
            self.rocket.engine_angle -= self.rocket.engine_angle_rate * dt
        
        # compute thrust vector
        thrust = Vector2(0.0, self.rocket.thrust_force_n)
        thrust.rotate_ip(self.rocket.rot_deg + self.rocket.engine_angle)

        self.rocket.accel += thrust / self.rocket.mass_kg # F = ma, a = F / m
        # gravity
        self.rocket.accel += self.gravity
        
        torque = Vector2(0, self.rocket.thrust_force_n).rotate(self.rocket.rot_deg + self.rocket.engine_angle).x * self.rocket.length_cm / 2
        self.rocket.angular_accel += torque / self.rocket.moment_inertia
        
        # apply angular accel
        self.rocket.angular_vel += self.rocket.angular_accel * dt
        self.rocket.rot_deg += self.rocket.angular_vel * dt
        
        # apply acceleration
        self.rocket.vel -= self.rocket.accel * dt
        self.rocket.pos += self.rocket.vel * dt
        
        self.rocket.max_height = max(self.rocket.max_height, -self.rocket.pos.y)

        # tick step
        self.paused = self.pause_on_next_tick == 1
        if self.pause_on_next_tick > 0:
            self.pause_on_next_tick -= 1
            print(self.pause_on_next_tick)