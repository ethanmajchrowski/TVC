[← Back to project README](../../README.md)
# Simulation

Simulation of the rocket initially began as a custom python program to simulate the gimbal and active control of the rocket. Due to the high complexity associated with writing such a program, this approach was discarded after a time of development. Future simulation will be done in MATLAB, but tuning of the PIDs for the rocket can be done using physical testing.

---

## Python Simulation
The flight simulation was written in Python using `pygame-ce`. It modeled the rocket's translational and rotational behavior and provided a development environment for testing the control system before flight.

The simulation included:

* Acceleration
* Velocity
* Position
* Thrust-vectoring torque
* PID control
* Estimated thrust-to-weight ratio
* Estimated apogee
* Simplified rocket-flight dynamics

![Flight Simulation](../../Images/sim.png)

*Python simulation interface and rocket-flight model.*