from icm20948 import ICM20948
import time
import csv
from datetime import datetime

imu = ICM20948(i2c_addr=0x69)
csv_file = 'imu_data.csv'

headers = ['Accel_X_g', 'Accel_Y_g', 'Accel_Z_g', 'Gyro_X_dps', 'Gyro_Y_dps', 'Gyro_Z_dps', 'Mag_X_uT', 'Mag_Y_uT', 'Mag_Z_uT', 'Temp', 'Timestamp']

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

		timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
		print(f"Accel: {ax:.2f}, {ay:.2f}, {az:.2f} g")
		print(f"Gyro: {gx:.2f}, {gy:.2f}, {gz:.2f} dps")
		print(f"Mag: {mx:.2f}, {my:.2f}, {mz:.2f} uT")
		print(f"Temp: {tmp:.2f}")
		data_row = [ax, ay, az, gx, gy, gz, mx, my, mz, tmp]
		data_row = [round(value, 5) for value in data_row]
		data_row.append(timestamp)

		with open(csv_file, 'a', newline='') as f:
			writer = csv.writer(f)
			writer.writerow(data_row)

		time.sleep(0.01)
except KeyboardInterrupt:
	print("\nStopped by user. Data saved to: ", csv_file)
