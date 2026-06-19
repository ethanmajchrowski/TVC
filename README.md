# Unnamed TVC Model Rocket
A model rocket featuring thrust vectoring, embedded control algorithms, and a physics simulation for tuning.

---

## Technical Specifications
* Liftoff Weight: TBD (approx. 250g)
* Motor Class: *target* Estes D12-5 *most likely* Estes E12-6, *last possible option* Estes F15-0
* Maximum TVC Gimbal Angle: approx. ±30 degrees
* Flight Computer: XIAO ESP32C6 (MicroPython)
* Sensors: IMU (MPU6050), Barometer (BMP280)

---

## System Architecture
### Mechanical Design (SolidWorks)
Mechanical hardware focuses on a lightweight TVC gimbal mount of 3 parts: outer mount (`/CAD/Parts/BodyGimbalMount.SLDPRT`), inner mount (`/CAD/Parts/Inner Gimal.SLDPRT`), and motor mount (`/CAD/Parts/MotorMount.SLDPRT`). These fit together giving 2 axes of rotation (x and y)
* All 3 gimbal parts are prinated in PETG for flexibility under stress
  * *PLA was used for prototyping but not for final design because it snaps under pressure while PETG bends more*

### Flight Simulation
Flight simulation written in python with pygame-ce. Emulates acceleration, velocity, and postiion of rocket body, computes torque from TVC gimbal, and includes other physical approximations of the rockets flight. 
* Emulates PID found on rocket so that it can be approximately tuned before any flight.
* Allows calculations of estimated apogee, TWR, and other flight characteristics. These are also calculated by a model of the rocket in the OpenRocket software. 

### Embedded Hardware
MicroPython running on the ESP32 present on the rocket's flight computer. 
* Sensor fusion: TBD
* Actuation: Servos update based on PWM from servo library
* Logging: telemetry is saved in the internal MicroPython OS at 100Hz (rate TBD)

---

## Gallery
[TVC Mount Cutaway](Images\Screenshot 2026-05-22 180708.png)
[TVC Isometric Cutaway](Images\Screenshot 2026-05-22 180623.png)
[TVC Isometric](Images\Screenshot 2026-05-22 180416.png)