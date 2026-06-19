# Example code for (GY-521) MPU6050 Accelerometer/Gyro Module
# Write in MicroPython by Warayut Poomiwatracanont JAN 2023

from MPU6050 import MPU6050

from os import listdir, chdir
from machine import Pin, I2C, SoftI2C
from time import sleep_ms

# i2c = I2C(0, sda=Pin(22), scl=Pin(23), freq=400000)
i2c = SoftI2C(sda=Pin(22), scl=Pin(23), freq=400000)
mpu = MPU6050(i2c)
print(f"devices set up! i2c scan: {i2c.scan()}")

while True:
    try:
        # Accelerometer Data
        accel = mpu.read_accel_data() # read the accelerometer [ms^-2]
        assert accel
        aX = accel["x"]
        aY = accel["y"]
        aZ = accel["z"]
        print("x: " + str(aX) + " y: " + str(aY) + " z: " + str(aZ))

        # Gyroscope Data
        # gyro = mpu.read_gyro_data()   # read the gyro [deg/s]
        # gX = gyro["x"]
        # gY = gyro["y"]
        # gZ = gyro["z"]
        # print("x:" + str(gX) + " y:" + str(gY) + " z:" + str(gZ))

        # Rough Temperature
        temp = mpu.read_temperature()   # read the device temperature [degC]
        # print("Temperature: " + str(temp) + "°C")

        # G-Force
        # gforce = mpu.read_accel_abs(g=True) # read the absolute acceleration magnitude
        # print("G-Force: " + str(gforce))

        # Time Interval Delay in millisecond (ms)
        sleep_ms(100)
    except KeyboardInterrupt:
        print("finish")
        break