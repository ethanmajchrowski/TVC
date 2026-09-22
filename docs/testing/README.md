[← Back to project README](../../README.md)
# Testing

## Test 01 - Thrust Simulation
In order to tune a PID properly, the system must be repeatedly tested and values tweaked to achieve the desired result. If the controller introduces oscillation or does not reach the setpoint within a desirable amount of time, the tuning constants must be adjusted. 

This project makes that process uniquely difficult. Due to the nature of rockets, the conditions in which the PID will be performing are difficult to replicate or repeat multiple times. To tune the rocket traditionally, it would have to be launched multiple times while examining the behavior of the control. This is costly and dangerous, as the rocket may not survive without a properly tuned algorithm.

To solve this problem, we can simulate the rocket's thrust using a propellor and drone motor. The plan for this test is to mount the rocket in a static gimbal that allows for rotation around the rocket's COM, then connect a motor and propellor to the motor mount. By spinning the propellor, we can simulate an equivalent thrust on the rocket. This allows us to test the mechanical performance of the gimbal mount as well as tune the control constants for the PID algorithms.

Testing is currently planned for the near future, as soon as the rocket CAD is finalized and initial assembly complete.