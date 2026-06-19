# need to 
- [x] Add some vis of engine gimbal
- [x] Take mass of rocket into account
- [x] Add torque from engine rotation
- [ ] Engine doesn't rotate instantly to setpoint
- [ ] Add PID to stabilize rocket (flight computer module? keep it isolated)
- [ ] Add sensor input so the PID gets imperfect data
  - measured_angle = true_angle + random.gauss(0, noise)

# want to 
- [ ] Aerodynamics?
  - [ ] Drag force
  - [ ] Center of pressure
  -  wind?
- [ ] Engine characteristics
  - ramp up
  - mass depletion
  - dynamic center of mass calcuation
- [ ] Servo limits (speed limits, latency, angle limits)
- simulation
  - [ ]  Pause / step frame
  - [ ]  Deterministic random seed