# need to 
- [ ] Add some vis of engine gimbal
- [ ] Take mass of rocket into account
- [ ] Add torque from engine rotation
- [ ] Add PID to stabilize rocket (flight computer module? keep it isolated)
- [ ] Add sensor input so the PID gets imperfect data
  - measured_angle = true_angle + random.gauss(0, noise)

# want to 
- [ ] Aerodynamics?
- [ ] Engine characteristics
  - ramp up
- [ ] Servo limits (speed limits, latency, angle limits)
- [ ] 