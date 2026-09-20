# Example code for (GY-521) MPU6050 Accelerometer/Gyro Module
# Write in MicroPython by Warayut Poomiwatracanont JAN 2023

from MPU6050 import MPU6050
from BMP280 import BMP280,BMP280_PRES_OS_16

from os import listdir, chdir
from machine import Pin, SoftI2C
from servo import Servo
import time
import math

class Pins:
    D0, D1, D2 = 0, 1, 2
    D3, D4, D5 = 21, 22, 23
    D6, D7 = 16, 17
    D8, D9, D10 = 19, 20, 18

# SETUP I2C and connected devices
SDA = Pin(Pins.D2)
SCL = Pin(Pins.D5)

i2c = SoftI2C(sda=SDA, scl=SCL, freq=100000)

mpu = MPU6050(i2c)
bmp = BMP280(i2c, use_case=BMP280_PRES_OS_16)

print(f"devices set up! i2c scan: {i2c.scan()}")

x_servo = Servo(Pins.D7)
x_servo_max = 100
y_servo = Servo(Pins.D9)
y_servo_max = 130
buzzer = Pin(Pins.D0, Pin.OUT)

# Globals
last_time = time.ticks_ms()
alpha = 0.98
roll, pitch, yaw = 0, 0, 0

alt_measurements = []

def clamp(val, lower, upper):
    return max(min(val, upper), lower)

class MultipurposePID:
    def __init__(self, KP, KD, KI, KI_MAX, MIN = None) -> None:
        '''
        Create a multipurpose PID that has individually tuned control variables.

        Args:
            KP (int): kP value for tuning controller
            KD (int): kD value for tuning controller
            KI (int): kI value for tuning controller
            KI_MAX (int): integral will not be allowed to pass this value
            MIN (int): a minimum value that the PID will output

        Returns:
            None
        '''
        
        self.kP, self.kD, self.kI = KP, KD, KI
        self.kI_max = KI_MAX
        self.error = 0
        self.integral = 0
        self.integral_processed = 0
        self.derivative = 0
        self.last_error = 0
        self.minimum = MIN
    def calculate(self, TARGET, INPUT) -> int:
        '''
        Calculates the output based on the PID's tuning and the provided target & input

        Args:
            TARGET (int): a number that the PID will try to reach
            INPUT (int): the current sensor or other input

        Returns:
            PID outpit (int)
        '''
        self.error = TARGET - INPUT

        if self.kI != 0:
            self.integral += self.error

            if self.integral > 0:
                self.integral = min(self.integral, 5 / self.kI)
            else:
                self.integral = max(self.integral, 5 / self.kI * -1)
            self.integral_processed = self.integral * self.kI

            if self.kI_max is not None:
                if self.integral_processed > 0:
                    self.integral_processed = min(self.integral_processed, self.kI_max)
                else:
                    self.integral_processed = max(self.integral_processed, self.kI_max * -1)

        self.derivative = (self.error - self.last_error) * self.kD
        
        output = (self.error * self.kP) + self.integral_processed + self.derivative
        if self.minimum is not None:
            if abs(output) < self.minimum:
                if self.error < 0: output = -self.minimum
                else: output = self.minimum
        
        self.last_error = self.error

        return output

class FlightController:
    def __init__(self) -> None:
        self.gyro_offsets = [0.0, 0.0, 0.0]
        self.pressure_baseline = 0.0
        self.last_orientation_time = None
        
        self.roll, self.yaw, self.pitch = 0.0, 0.0, 0.0
        print("Created flight controller object")

    def calibrate(self, calibration_time: int = 10):
        print("Calibrating IMU & altimeter")

        offsets = [0.0, 0.0, 0.0]
        baseline_pressure = 0
        
        num_measurements = 0
        end_loop_time = time.time() + calibration_time
        while time.time() < end_loop_time:
            num_measurements += 1
            offsets += self.get_gyro()
            baseline_pressure += bmp.pressure
        
            time.sleep(0.05)
        
        print(f"Sensor calibration complete. Collected {num_measurements} points")
        self.gyro_offsets = [i/num_measurements for i in offsets]
        self.pressure_baseline = baseline_pressure / num_measurements

    def update_orientation(self):
        ax, ay, az = self.get_accel()
        gx, gy, gz = self.get_gyro()
        

        now = time.ticks_ms()
        if not self.last_orientation_time: self.last_orientation_time = now
        
        dt = (time.ticks_diff(now, self.last_orientation_time )) / 1000
        self.last_orientation_time  = now

        # convert gyro deg/s -> rad/s
        gx = math.radians(gx - self.gyro_offsets[0])
        gy = math.radians(gy - self.gyro_offsets[1])
        gz = math.radians(gz - self.gyro_offsets[2])

        # --- gyro integration ---
        self.roll += gx * dt
        self.pitch += gy * dt
        self.yaw += gz * dt

        # --- accel angles ---
        accel_roll = math.atan2(ay, az)
        accel_pitch = math.atan2(-ax, math.sqrt(ay*ay + az*az))

        # --- complementary filter ---
        self.roll = alpha * self.roll + (1 - alpha) * accel_roll
        self.pitch = alpha * self.pitch + (1 - alpha) * accel_pitch

        self.max_altitude = 0


    @staticmethod
    def get_gyro():
        gyro = mpu.read_gyro_data()   # read the gyro [deg/s]
        assert gyro
        return gyro["x"], gyro["y"], gyro["z"]

    @staticmethod
    def get_accel():
        accel = mpu.read_accel_data()
        assert accel
        return accel["x"], accel["y"], accel["z"]
    
    @staticmethod
    def update_servo(deg: float | int, servo: Servo, msg: bool = False):
        if msg: print(f"spinning servo to {deg} deg")
        servo.write(deg)

    def get_altitude(self):
        R = 287.05
        T = bmp.temperature + 273.15
        g = 9.80665
        k = R * T / g
        relative_alt = k * math.log(self.pressure_baseline / bmp.pressure)
        
        alt_measurements.insert(0, relative_alt)
        if len(alt_measurements) >= 10:
            alt_measurements.pop()
        
        return sum(alt_measurements) / len(alt_measurements)

    @staticmethod
    def beep(sound_time: float = 0.05):
        buzzer.on()
        time.sleep(sound_time)
        buzzer.off()

    def circle_servo_test(self, duration: int = 10):
        last_time = time.ticks_ms()
        elapsed_time = 0
        
        while elapsed_time < duration:
            elapsed_time += time.ticks_diff(time.ticks_ms(), last_time) / 1000
            last_time = time.ticks_ms()
            
            y_pos = (math.sin(elapsed_time * 3.0)+ 1.0) / 2
            self.update_servo(y_pos * y_servo_max, y_servo)

            x_pos = (math.cos(elapsed_time * 3.0)+ 1.0) / 2
            self.update_servo(x_pos * x_servo_max, x_servo)
            # print(y_pos, x_pos)

    def run_timed(self, duration: int = 20):
        start_time = time.ticks_ms()
        print(f"Running {duration}s timed run")
        # self.beep()
        time.sleep(0.5)
        self.beep(0.1)
        
        self.update_servo(x_servo_max / 2, x_servo)
        self.update_servo(y_servo_max / 2, y_servo)
        
        # timed vars
        last_time = time.ticks_ms()
        elapsed_time = 0

        x_pid = MultipurposePID(0.3, 0.01, 0.0, 0.0)
        y_pid = MultipurposePID(0.3, 0.01, 0.0, 0.0)
        
        while elapsed_time < duration:
            elapsed_time += time.ticks_diff(time.ticks_ms(), last_time) / 1000
            last_time = time.ticks_ms()
            
            self.update_orientation()
            
            # self.pitch and self.roll are from -1.5 to 1.5 (1.5 being 90 degrees, so if it gets that bad we cant do anything)
            # normalize raw pitch and roll data to be from 0 to max servo angle

            # print((self.pitch + 1.5) / 3.0)
            # print(x_servo_max)
            normalized_pitch = ((self.pitch + 1.5) / 3.0) * x_servo_max
            normalized_yaw = ((self.roll + 1.5) / 3.0) * y_servo_max
                        
            x_out = x_pid.calculate(x_servo_max / 2, normalized_pitch)
            y_out = y_pid.calculate(y_servo_max / 2, normalized_yaw)
            
            x_target = x_servo.read() + x_out
            y_target = y_servo.read() + y_out
            # self.update_servo(x_out, x_servo)
            self.update_servo(clamp(x_target, 0, x_servo_max), x_servo)
            self.update_servo(clamp(y_target, 0, y_servo_max), y_servo)
            # print(x_target)
            # print(self.pitch, self.roll)
            alt = self.get_altitude()
            self.max_altitude = max(alt, self.max_altitude)
        
        print("Timed run complete, beeping.")
        self.beep()
        
        print("Writing data to flight log.")
        with open("log.txt", "w") as f:
            f.write(f"max alt: {self.max_altitude}\n")
            f.write(f"Start time: {start_time}ms\n")
            f.write(f"End time: {str(time.ticks_ms())}ms\n")
            f.write(f"Elapsed time: {str(time.ticks_diff(time.ticks_ms(), start_time))}")
        print("Done writing data!")
    
    def run(self):
        self.beep()
        
        # servo test
        # print("testing servo motors")
        
        self.update_servo(x_servo_max // 2, x_servo)
        self.update_servo(y_servo_max // 2, y_servo)

        x_pid = MultipurposePID(0.1, 0.0, 0.0, 0.0)

        # self.update_servo(0, servo1)
        # self.update_servo(0, servo2)
        # self.update_servo(x_servo_max//2, x_servo)
        # self.update_servo(y_servo_max, x_servo)
        # self.update_servo(y_servo_max//2, y_servo)

        # time.sleep(1)
        # # self.update_servo(125, servo1)
        # self.update_servo(125//2, servo1)
        # time.sleep(2)
        # # self.update_servo(0, servo1)
        # time.sleep(1)
        # self.update_servo(90, servo2)
        # time.sleep(2)
        # self.update_servo(0, servo2)
        # time.sleep(1)
        # self.update_servo(50, servo2)
        # time.sleep(1)
        # self.update_servo(180, servo2)
        # time.sleep(1)
        # self.update_servo(0, servo2)
        
        # print('started')
        # while True:
        #     print(bmp.temperature)

        # while True:
        #     try:
        #         # self.update_orientation()
                
        #         # print(f"{self.roll}, {self.pitch}, {self.yaw}, {self.get_altitude()}")

        #         # # Rough Temperature
        #         # temp = mpu.read_temperature()   # read the device temperature [degC]
        #         # print("Temperature: " + str(temp) + "°C")

        #         # # G-Force
        #         # gforce = mpu.read_accel_abs(g=True) # read the absolute acceleration magnitude
        #         # print("G-Force: " + str(gforce))
                
        #         time.sleep_ms(100)
        #     except KeyboardInterrupt:
        #         print("stopped")
        #         break
        
        print("done")

if __name__ == "__main__":
    con = FlightController()
    con.beep()
    con.calibrate(5)
    # con.run()
    # con.circle_servo_test(10)
    con.run_timed(10)
    con.beep()