from icm20948 import ICM20948
import time
import csv
import serial
from datetime import datetime
import struct
import numpy as np

imu = ICM20948(i2c_addr=0x69)
csv_file = 'imu_data.csv'
ser = serial.Serial('/dev/ttyS0', 420000, timeout=1)

headers = ['Accel_X_g', 'Accel_Y_g', 'Accel_Z_g', 'Gyro_X_dps', 'Gyro_Y_dps', 'Gyro_Z_dps',
           'Mag_X_uT', 'Mag_Y_uT', 'Mag_Z_uT', 'Temp', 'Timestamp']

def clamp_to_float32(val):
    try:
        fval = float(val)
        if np.isnan(fval) or np.isinf(fval):
            return 0.0
        vmin, vmax = np.finfo(np.float32).min, np.finfo(np.float32).max
        return max(min(fval, vmax), vmin)
    except:
        return 0.0

def crsf_crc(payload):
    crc = 0
    for b in payload:
        crc ^= b
    return crc

def send_imu_with_timestamp_as_crsf(timestamp_us, ax, ay, az, gx, gy, gz, mx, my, mz, tmp):
    payload_id = 0xF0
    timestamp_us = int(timestamp_us) & 0xFFFFFFFF #ensure timestamp is uint32
    L = [ax, ay, az, gx, gy, gz, mx, my, mz, tmp]
    L = [clamp_to_float32(x) for x in L]  
    payload = struct.pack('<BIffffffffff', payload_id, timestamp_us, *L)
    print(timestamp_us, *L)  # debug
    frame = struct.pack('<BB', 0xC8, len(payload)) + payload
    crc = crsf_crc(frame[2:])   
    frame += bytes([crc])
    ser.write(frame)

try:
    with open(csv_file, 'x', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
except FileExistsError:
    pass
print(f"Saving data to {csv_file}")

try:
    while True:
        ax, ay, az, gx, gy, gz = imu.read_accelerometer_gyro_data()
        mx, my, mz = imu.read_magnetometer_data()
        tmp = imu.read_temperature()
        
        timestamp_dt = datetime.now()
        timestamp = timestamp_dt.strftime('%Y-%m-%d %H:%M:%S.%f')
        timestamp_us = int(timestamp_dt.timestamp() * 1_000_000)

        data_row = [ax, ay, az, gx, gy, gz, mx, my, mz, tmp]
        data_row = [round(value, 4) for value in data_row]
        data_row.append(timestamp)

        with open(csv_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(data_row)

        
        send_imu_with_timestamp_as_crsf(timestamp_us, float(ax), float(ay), float(az),
                                        float(gx), float(gy), float(gz),
                                        float(mx), float(my), float(mz),
                                        float(tmp))



#        print(f"Accel: {ax:.2f}, {ay:.2f}, {az:.2f} g")
#        print(f"Gyro: {gx:.2f}, {gy:.2f}, {gz:.2f} dps")
#        print(f"Mag: {mx:.2f}, {my:.2f}, {mz:.2f} uT")
#        print(f"Temp: {tmp:.2f}")
#        print(f"Timestamp: {timestamp}, us={timestamp_us}")
        time.sleep(0.05)

except KeyboardInterrupt:
    ser.close()
    print("\nStopped by user. Data saved to:", csv_file)
