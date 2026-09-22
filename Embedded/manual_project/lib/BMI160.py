from machine import I2C
from utime import sleep_ms
import struct

#region Constants
# BMI160 register map and constants for MicroPython driver

# Core registers
RA_CHIP_ID       = 0x00
RA_PMU_STATUS    = 0x03

# Data registers
RA_GYRO_X_L, RA_GYRO_X_H = 0x0C, 0x0D
RA_GYRO_Y_L, RA_GYRO_Y_H = 0x0E, 0x0F
RA_GYRO_Z_L, RA_GYRO_Z_H = 0x10, 0x11
RA_ACCEL_X_L, RA_ACCEL_X_H = 0x12, 0x13
RA_ACCEL_Y_L, RA_ACCEL_Y_H = 0x14, 0x15
RA_ACCEL_Z_L, RA_ACCEL_Z_H = 0x16, 0x17

RA_STATUS        = 0x1B

# Interrupt status
RA_INT_STATUS_0  = 0x1C
RA_INT_STATUS_1  = 0x1D
RA_INT_STATUS_2  = 0x1E
RA_INT_STATUS_3  = 0x1F

# Configuration
RA_ACCEL_CONF    = 0x40
RA_ACCEL_RANGE   = 0x41
RA_GYRO_CONF     = 0x42
RA_GYRO_RANGE    = 0x43

RA_FIFO_LENGTH_0 = 0x22
RA_FIFO_LENGTH_1 = 0x23
RA_FIFO_DATA     = 0x24

# Interrupt enables and routing
RA_INT_EN_0      = 0x50
RA_INT_EN_1      = 0x51
RA_INT_EN_2      = 0x52
RA_INT_OUT_CTRL  = 0x53
RA_INT_LATCH     = 0x54
RA_INT_MAP_0     = 0x55
RA_INT_MAP_1     = 0x56
RA_INT_MAP_2     = 0x57

# Motion and tap config
RA_INT_MOTION_0  = 0x5F
RA_INT_MOTION_1  = 0x60
RA_INT_MOTION_2  = 0x61
RA_INT_MOTION_3  = 0x62
RA_INT_TAP_0     = 0x63
RA_INT_TAP_1     = 0x64

# Command register
RA_CMD           = 0x7E
RA_FOC_CONF      = 0x69

# Offset compensation registers
RA_OFFSET_0      = 0x71  # Accel X offset (8-bit, 3.9mg/LSB)
RA_OFFSET_1      = 0x72  # Accel Y offset
RA_OFFSET_2      = 0x73  # Accel Z offset
RA_OFFSET_3      = 0x74  # Gyro X offset low (LSB 8 bits)
RA_OFFSET_4      = 0x75  # Gyro Y offset low
RA_OFFSET_5      = 0x76  # Gyro Z offset low
RA_OFFSET_6      = 0x77  # Offset enable bits + gyro MSBs

# Bit fields
ACC_PMU_STATUS_BIT, ACC_PMU_STATUS_LEN = 4, 2
GYR_PMU_STATUS_BIT, GYR_PMU_STATUS_LEN = 2, 2

ACCEL_RATE_SEL_BIT, ACCEL_RATE_SEL_LEN = 0, 4
ACCEL_RANGE_SEL_BIT, ACCEL_RANGE_SEL_LEN = 0, 4
GYRO_RATE_SEL_BIT,  GYRO_RATE_SEL_LEN  = 0, 4
GYRO_RANGE_SEL_BIT, GYRO_RANGE_SEL_LEN = 0, 3

ANYMOTION_EN_BIT, ANYMOTION_EN_LEN = 0, 3  # X/Y/Z enable bits in INT_EN_0
D_TAP_EN_BIT, S_TAP_EN_BIT = 4, 5

INT1_LVL, INT1_OD, INT1_OUTPUT_EN = 1, 2, 3
LATCH_MODE_BIT, LATCH_MODE_LEN = 0, 4

# Interrupt status bits
ANYMOTION_INT_BIT = 2
D_TAP_INT_BIT, S_TAP_INT_BIT = 4, 5

# Motion duration bits (for ANYMOTION_DUR in INT_MOTION_0)
ANYMOTION_DUR_BIT, ANYMOTION_DUR_LEN = 0, 2

# Status bits
# Fast Offset Compensation (FOC) ready bit in RA_STATUS
STATUS_FOC_RDY_BIT = 3

# FOC config bits in RA_FOC_CONF
FOC_ACC_Z_BIT, FOC_ACC_Z_LEN = 0, 2
FOC_ACC_Y_BIT, FOC_ACC_Y_LEN = 2, 2
FOC_ACC_X_BIT, FOC_ACC_X_LEN = 4, 2
FOC_GYR_EN_BIT = 6

# Offset enable bits in RA_OFFSET_6
ACC_OFFSET_EN_BIT = 6
GYR_OFFSET_EN_BIT = 7

# Gyro offset MSB fields in RA_OFFSET_6
GYR_OFFSET_X_MSB_BIT, GYR_OFFSET_X_MSB_LEN = 0, 2
GYR_OFFSET_Y_MSB_BIT, GYR_OFFSET_Y_MSB_LEN = 2, 2
GYR_OFFSET_Z_MSB_BIT, GYR_OFFSET_Z_MSB_LEN = 4, 2

# Enums/mappings
ACC_RANGE_REG = {2: 0x03, 4: 0x05, 8: 0x08, 16: 0x0C}
GYR_RANGE_REG = {2000: 0, 1000: 1, 500: 2, 250: 3, 125: 4}
ACC_ODR_REG   = {12.5: 5, 25: 6, 50: 7, 100: 8, 200: 9, 400: 10, 800: 11, 1600: 12}
GYR_ODR_REG   = {25: 6, 50: 7, 100: 8, 200: 9, 400: 10, 800: 11, 1600: 12, 3200: 13}

# Latch modes
LATCH_MODE = {
    'NONE': 0,
    '312_US': 1,
    '625_US': 2,
    '1_25_MS': 3,
    '2_5_MS': 4,
    '5_MS': 5,
    '10_MS': 6,
    '20_MS': 7,
    '40_MS': 8,
    '80_MS': 9,
    '160_MS': 10,
    '320_MS': 11,
    '640_MS': 12,
    '1_28_S': 13,
    '2_56_S': 14,
    'LATCH': 15,
}

# mg-per-LSB for any-motion threshold by accel range
MOTION_MG_LSB = {2: 3.91, 4: 7.81, 8: 15.63, 16: 31.25}

# Commands
CMD_SOFT_RESET       = 0xB6
CMD_ACC_MODE_NORMAL  = 0x11
CMD_GYR_MODE_NORMAL  = 0x15
CMD_INT_RESET        = 0xB1
CMD_START_FOC        = 0x03

#endregion Constants


def _read_bits(val, pos, length):
    mask = (1 << length) - 1
    return (val >> pos) & mask


def _write_bits(orig, data, pos, length):
    mask = ((1 << length) - 1) << pos
    data = (data << pos) & mask
    return (orig & ~mask) | data


class BMI160:
    def __init__(self, i2c: I2C, addr: int = 0x68):
        self.i2c = i2c
        self.addr = addr
        self.acc_range_g = 2
        self.acc_odr_hz = 100
        self.gyr_range_dps = 250

    # ---------------- low-level io ----------------
    def _read_u8(self, reg):
        return self.i2c.readfrom_mem(self.addr, reg, 1)[0]

    def _write_u8(self, reg, val):
        self.i2c.writeto_mem(self.addr, reg, bytes([val & 0xFF]))

    def _read_block(self, reg, length):
        return self.i2c.readfrom_mem(self.addr, reg, length)

    def _update_bits(self, reg, pos, length, data):
        orig = self._read_u8(reg)
        newv = _write_bits(orig, data, pos, length)
        if newv != orig:
            self._write_u8(reg, newv)

    @staticmethod
    def _sign_extend(val, bits):
        sign = 1 << (bits - 1)
        return (val & (sign - 1)) - (val & sign)

    # ---------------- init and setup ----------------
    def initialize(self):
        # Soft reset
        self._write_u8(RA_CMD, CMD_SOFT_RESET)
        sleep_ms(2)

        # Power up ACC
        self._write_u8(RA_CMD, CMD_ACC_MODE_NORMAL)
        sleep_ms(2)
        # Wait until ACC ready
        for _ in range(50):
            pmu = self._read_u8(RA_PMU_STATUS)
            if _read_bits(pmu, ACC_PMU_STATUS_BIT, ACC_PMU_STATUS_LEN) == 0x1:
                break
            sleep_ms(2)

        # Power up GYR
        self._write_u8(RA_CMD, CMD_GYR_MODE_NORMAL)
        sleep_ms(2)
        for _ in range(50):
            pmu = self._read_u8(RA_PMU_STATUS)
            if _read_bits(pmu, GYR_PMU_STATUS_BIT, GYR_PMU_STATUS_LEN) == 0x1:
                break
            sleep_ms(2)

        # Defaults
        self.set_accel_range(2)
        self.set_accel_rate(100)
        self.set_gyro_range(250)
        self.set_gyro_rate(100)

        # Map all INT sources to INT1 similar to Arduino lib
        self._write_u8(RA_INT_MAP_0, 0xFF)
        self._write_u8(RA_INT_MAP_1, 0xF0)
        self._write_u8(RA_INT_MAP_2, 0x00)

    # --------------- accel/gyro config ---------------
    def set_accel_range(self, g: int):
        code = ACC_RANGE_REG.get(g)
        if code is None:
            raise ValueError("invalid accel range")
        self._update_bits(RA_ACCEL_RANGE, ACCEL_RANGE_SEL_BIT, ACCEL_RANGE_SEL_LEN, code)
        self.acc_range_g = g

    def set_accel_rate(self, hz: float):
        code = ACC_ODR_REG.get(hz)
        if code is None:
            raise ValueError("invalid accel rate")
        self._update_bits(RA_ACCEL_CONF, ACCEL_RATE_SEL_BIT, ACCEL_RATE_SEL_LEN, code)
        self.acc_odr_hz = hz

    def set_gyro_range(self, dps: int):
        code = GYR_RANGE_REG.get(dps)
        if code is None:
            raise ValueError("invalid gyro range")
        self._update_bits(RA_GYRO_RANGE, GYRO_RANGE_SEL_BIT, GYRO_RANGE_SEL_LEN, code)
        self.gyr_range_dps = dps

    def set_gyro_rate(self, hz: float):
        code = GYR_ODR_REG.get(hz)
        if code is None:
            raise ValueError("invalid gyro rate")
        self._update_bits(RA_GYRO_CONF, GYRO_RATE_SEL_BIT, GYRO_RATE_SEL_LEN, code)

    # --------------- data read ---------------
    @staticmethod
    def _to_int16(lo, hi):
        val = (hi << 8) | lo
        if val & 0x8000:
            val -= 0x10000
        return val

    def read_accel_raw(self):
        b = self._read_block(RA_ACCEL_X_L, 6)
        ax = self._to_int16(b[0], b[1])
        ay = self._to_int16(b[2], b[3])
        az = self._to_int16(b[4], b[5])
        return ax, ay, az

    def read_gyro_raw(self):
        b = self._read_block(RA_GYRO_X_L, 6)
        gx = self._to_int16(b[0], b[1])
        gy = self._to_int16(b[2], b[3])
        gz = self._to_int16(b[4], b[5])
        return gx, gy, gz

    # Unit scaling helpers
    def _acc_lsb_per_g(self):
        if self.acc_range_g == 2:
            return 16384.0
        if self.acc_range_g == 4:
            return 8192.0
        if self.acc_range_g == 8:
            return 4096.0
        return 2048.0  # 16g

    def _gyr_lsb_per_dps(self):
        if self.gyr_range_dps == 125:
            return 262.144
        if self.gyr_range_dps == 250:
            return 131.072
        if self.gyr_range_dps == 500:
            return 65.536
        if self.gyr_range_dps == 1000:
            return 32.768
        return 16.384  # 2000 dps

    def read_accel(self):
        ax, ay, az = self.read_accel_raw()
        s = self._acc_lsb_per_g()
        return ax / s, ay / s, az / s

    def read_gyro(self) -> tuple[float, float, float]:
        gx, gy, gz = self.read_gyro_raw()
        s = self._gyr_lsb_per_dps()
        return gx / s, gy / s, gz / s

    # --------------- interrupts ---------------
    def set_int_output(self, active_low=True, open_drain=False, enable=True):
        v = self._read_u8(RA_INT_OUT_CTRL)
        v = _write_bits(v, 1 if active_low else 0, INT1_LVL, 1)
        v = _write_bits(v, 1 if open_drain else 0, INT1_OD, 1)
        v = _write_bits(v, 1 if enable else 0, INT1_OUTPUT_EN, 1)
        self._write_u8(RA_INT_OUT_CTRL, v)

    def set_int_latch(self, mode_key='320_MS'):
        mode = LATCH_MODE.get(mode_key, LATCH_MODE['320_MS'])
        v = self._read_u8(RA_INT_LATCH)
        v = _write_bits(v, mode, LATCH_MODE_BIT, LATCH_MODE_LEN)
        self._write_u8(RA_INT_LATCH, v)

    def enable_any_motion(self, enable=True):
        # Enable X, Y, Z in INT_EN_0
        val = 0x7 if enable else 0x0
        v = self._read_u8(RA_INT_EN_0)
        v = _write_bits(v, val, ANYMOTION_EN_BIT, ANYMOTION_EN_LEN)
        self._write_u8(RA_INT_EN_0, v)

    def set_motion_threshold_mg(self, mg: float):
        step = MOTION_MG_LSB.get(self.acc_range_g, 3.91)
        thr = int(mg / step)
        if thr < 0:
            thr = 0
        if thr > 255:
            thr = 255
        self._write_u8(RA_INT_MOTION_1, thr)

    def set_motion_duration_s(self, seconds: float):
        samples = int(round(seconds * self.acc_odr_hz))
        if samples < 1:
            samples = 1
        if samples > 4:
            samples = 4
        # Stored as samples-1 in ANYMOTION_DUR bits (ahora usando constantes como C)
        v = self._read_u8(RA_INT_MOTION_0)
        v = _write_bits(v, samples - 1, ANYMOTION_DUR_BIT, ANYMOTION_DUR_LEN)
        self._write_u8(RA_INT_MOTION_0, v)

    def motion_triggered(self) -> bool:
        st = self._read_u8(RA_INT_STATUS_0)
        return bool(_read_bits(st, ANYMOTION_INT_BIT, 1))

    def reset_interrupt(self):
        self._write_u8(RA_CMD, CMD_INT_RESET)
    
    # Funciones adicionales para coincidir exactamente con el código C
    def set_tap_enabled(self, enable=False):
        """Equivalente a BMI160.setIntTapEnabled(false)"""
        v = self._read_u8(RA_INT_EN_0)
        v = _write_bits(v, 1 if enable else 0, S_TAP_EN_BIT, 1)
        self._write_u8(RA_INT_EN_0, v)
    
    def set_double_tap_enabled(self, enable=False):
        """Equivalente a BMI160.setIntDoubleTapEnabled(false)"""
        v = self._read_u8(RA_INT_EN_0)
        v = _write_bits(v, 1 if enable else 0, D_TAP_EN_BIT, 1)
        self._write_u8(RA_INT_EN_0, v)

    # --------------- calibration & offsets ---------------
    # Accelerometer offset compensation enable
    def get_accel_offset_enabled(self):
        v = self._read_u8(RA_OFFSET_6)
        return bool(_read_bits(v, ACC_OFFSET_EN_BIT, 1))

    def set_accel_offset_enabled(self, enabled: bool):
        self._update_bits(RA_OFFSET_6, ACC_OFFSET_EN_BIT, 1, 1 if enabled else 0)

    # Gyroscope offset compensation enable
    def get_gyro_offset_enabled(self):
        v = self._read_u8(RA_OFFSET_6)
        return bool(_read_bits(v, GYR_OFFSET_EN_BIT, 1))

    def set_gyro_offset_enabled(self, enabled: bool):
        self._update_bits(RA_OFFSET_6, GYR_OFFSET_EN_BIT, 1, 1 if enabled else 0)

    # Auto-calibration (FOC) for accelerometer per axis
    def auto_calibrate_x_accel_offset(self, target: int):
        # target: 0 -> 0g, 1 -> +1g, -1 -> -1g
        if target == 1:
            conf = (0x1 << FOC_ACC_X_BIT)
        elif target == -1:
            conf = (0x2 << FOC_ACC_X_BIT)
        elif target == 0:
            conf = (0x3 << FOC_ACC_X_BIT)
        else:
            return
        self._write_u8(RA_FOC_CONF, conf)
        self._write_u8(RA_CMD, CMD_START_FOC)
        while not _read_bits(self._read_u8(RA_STATUS), STATUS_FOC_RDY_BIT, 1):
            sleep_ms(1)

    def auto_calibrate_y_accel_offset(self, target: int):
        if target == 1:
            conf = (0x1 << FOC_ACC_Y_BIT)
        elif target == -1:
            conf = (0x2 << FOC_ACC_Y_BIT)
        elif target == 0:
            conf = (0x3 << FOC_ACC_Y_BIT)
        else:
            return
        self._write_u8(RA_FOC_CONF, conf)
        self._write_u8(RA_CMD, CMD_START_FOC)
        while not _read_bits(self._read_u8(RA_STATUS), STATUS_FOC_RDY_BIT, 1):
            sleep_ms(1)

    def auto_calibrate_z_accel_offset(self, target: int):
        if target == 1:
            conf = (0x1 << FOC_ACC_Z_BIT)
        elif target == -1:
            conf = (0x2 << FOC_ACC_Z_BIT)
        elif target == 0:
            conf = (0x3 << FOC_ACC_Z_BIT)
        else:
            return
        self._write_u8(RA_FOC_CONF, conf)
        self._write_u8(RA_CMD, CMD_START_FOC)
        while not _read_bits(self._read_u8(RA_STATUS), STATUS_FOC_RDY_BIT, 1):
            sleep_ms(1)

    # Auto-calibration (FOC) for gyro (all axes)
    def auto_calibrate_gyro_offset(self):
        conf = (1 << FOC_GYR_EN_BIT)
        self._write_u8(RA_FOC_CONF, conf)
        self._write_u8(RA_CMD, CMD_START_FOC)
        while not _read_bits(self._read_u8(RA_STATUS), STATUS_FOC_RDY_BIT, 1):
            sleep_ms(1)

    # Manual accel offsets (8-bit, 3.9mg/LSB)
    def get_x_accel_offset(self):
        v = self._read_u8(RA_OFFSET_0)
        return v if v < 128 else v - 256

    def set_x_accel_offset(self, offset: int):
        self._write_u8(RA_OFFSET_0, offset & 0xFF)

    def get_y_accel_offset(self):
        v = self._read_u8(RA_OFFSET_1)
        return v if v < 128 else v - 256

    def set_y_accel_offset(self, offset: int):
        self._write_u8(RA_OFFSET_1, offset & 0xFF)

    def get_z_accel_offset(self):
        v = self._read_u8(RA_OFFSET_2)
        return v if v < 128 else v - 256

    def set_z_accel_offset(self, offset: int):
        self._write_u8(RA_OFFSET_2, offset & 0xFF)

    # Manual gyro offsets (10-bit two's complement, 0.061 dps/LSB)
    def get_x_gyro_offset(self):
        lo = self._read_u8(RA_OFFSET_3)
        msb = _read_bits(self._read_u8(RA_OFFSET_6), GYR_OFFSET_X_MSB_BIT, GYR_OFFSET_X_MSB_LEN)
        raw = lo | (msb << 8)
        return self._sign_extend(raw, 10)

    def set_x_gyro_offset(self, offset: int):
        raw = offset & 0x3FF
        self._write_u8(RA_OFFSET_3, raw & 0xFF)
        self._update_bits(RA_OFFSET_6, GYR_OFFSET_X_MSB_BIT, GYR_OFFSET_X_MSB_LEN, (raw >> 8) & 0x3)

    def get_y_gyro_offset(self):
        lo = self._read_u8(RA_OFFSET_4)
        msb = _read_bits(self._read_u8(RA_OFFSET_6), GYR_OFFSET_Y_MSB_BIT, GYR_OFFSET_Y_MSB_LEN)
        raw = lo | (msb << 8)
        return self._sign_extend(raw, 10)

    def set_y_gyro_offset(self, offset: int):
        raw = offset & 0x3FF
        self._write_u8(RA_OFFSET_4, raw & 0xFF)
        self._update_bits(RA_OFFSET_6, GYR_OFFSET_Y_MSB_BIT, GYR_OFFSET_Y_MSB_LEN, (raw >> 8) & 0x3)

    def get_z_gyro_offset(self):
        lo = self._read_u8(RA_OFFSET_5)
        msb = _read_bits(self._read_u8(RA_OFFSET_6), GYR_OFFSET_Z_MSB_BIT, GYR_OFFSET_Z_MSB_LEN)
        raw = lo | (msb << 8)
        return self._sign_extend(raw, 10)

    def set_z_gyro_offset(self, offset: int):
        raw = offset & 0x3FF
        self._write_u8(RA_OFFSET_5, raw & 0xFF)
        self._update_bits(RA_OFFSET_6, GYR_OFFSET_Z_MSB_BIT, GYR_OFFSET_Z_MSB_LEN, (raw >> 8) & 0x3)

    # CamelCase aliases to mirror C API names (optional convenience)
    def getAccelOffsetEnabled(self):
        return self.get_accel_offset_enabled()

    def setAccelOffsetEnabled(self, enabled: bool):
        self.set_accel_offset_enabled(enabled)

    def getGyroOffsetEnabled(self):
        return self.get_gyro_offset_enabled()

    def setGyroOffsetEnabled(self, enabled: bool):
        self.set_gyro_offset_enabled(enabled)

    def autoCalibrateXAccelOffset(self, target: int):
        self.auto_calibrate_x_accel_offset(target)

    def autoCalibrateYAccelOffset(self, target: int):
        self.auto_calibrate_y_accel_offset(target)

    def autoCalibrateZAccelOffset(self, target: int):
        self.auto_calibrate_z_accel_offset(target)

    def autoCalibrateGyroOffset(self):
        self.auto_calibrate_gyro_offset()

    def getXAccelOffset(self):
        return self.get_x_accel_offset()

    def setXAccelOffset(self, offset: int):
        self.set_x_accel_offset(offset)

    def getYAccelOffset(self):
        return self.get_y_accel_offset()

    def setYAccelOffset(self, offset: int):
        self.set_y_accel_offset(offset)

    def getZAccelOffset(self):
        return self.get_z_accel_offset()

    def setZAccelOffset(self, offset: int):
        self.set_z_accel_offset(offset)

    def getXGyroOffset(self):
        return self.get_x_gyro_offset()

    def setXGyroOffset(self, offset: int):
        self.set_x_gyro_offset(offset)

    def getYGyroOffset(self):
        return self.get_y_gyro_offset()

    def setYGyroOffset(self, offset: int):
        self.set_y_gyro_offset(offset)

    def getZGyroOffset(self):
        return self.get_z_gyro_offset()

    def setZGyroOffset(self, offset: int):
        self.set_z_gyro_offset(offset)