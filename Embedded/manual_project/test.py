# Example code for (GY-521) MPU6050 Accelerometer/Gyro Module
# Write in MicroPython by Warayut Poomiwatracanont JAN 2023

# from MPU6050 import MPU6050
from BMI160 import BMI160

from os import listdir, chdir
from machine import Pin, I2C, SoftI2C
from time import sleep_ms

# i2c = I2C(0, sda=Pin(22), scl=Pin(23), freq=400000)
i2c = SoftI2C(sda=Pin(22), scl=Pin(23), freq=400000)
IMU = BMI160(i2c, addr=105)
print(f"devices set up! i2c scan: {i2c.scan()}")
print(IMU.read_gyro_raw())

IMU.initialize()

IMU.set_gyro_offset_enabled(True)

IMU.auto_calibrate_gyro_offset()
IMU.set_gyro_range(250)
IMU.set_gyro_rate(100.0)

rotation = [0.0, 0.0, 0.0]

while True:
    try:
        # Accelerometer Data
        gyro = IMU.read_gyro() # read the accelerometer [ms^-2]
        assert gyro is not None
        rotation[0] += gyro[0] / 100
        rotation[1] += gyro[1] / 100
        rotation[2] += gyro[2] / 100
        print("{:.2f}, {:.2f}, {:.2f}".format(*rotation))
        # aX = accel["x"] # type: ignore
        # aY = accel["y"] # type: ignore
        # aZ = accel["z"] # type: ignore
        # print("x: " + str(aX) + " y: " + str(aY) + " z: " + str(aZ))

        # Gyroscope Data
        # gyro = mpu.read_gyro_data()   # read the gyro [deg/s]
        # gX = gyro["x"]
        # gY = gyro["y"]
        # gZ = gyro["z"]
        # print("x:" + str(gX) + " y:" + str(gY) + " z:" + str(gZ))

        # Rough Temperature
        # temp = mpu.read_temperature()   # read the device temperature [degC]
        # print("Temperature: " + str(temp) + "°C")

        # G-Force
        # gforce = mpu.read_accel_abs(g=True) # read the absolute acceleration magnitude
        # print("G-Force: " + str(gforce))

        # Time Interval Delay in millisecond (ms)
        sleep_ms(10)
    except KeyboardInterrupt:
        print("finish")
        break