import time, board, busio
import adafruit_bmp280
from collections import deque
import os

i2c = busio.I2C(board.SCL, board.SDA)
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x77)
bmp280.sea_level_pressure = 1013.25

time.sleep(0.5)

init_alt = bmp280.altitude
window = 4
buf = deque(maxlen=window)
sma = 0.0
n = 0

hz = 50
dt = 1.0 / hz

fname = 'alt_log.txt'
if not os.path.exists(fname):
    with open(fname, 'w') as f:
        pass

f = open(fname, 'a', buffering=1)
t0 = time.monotonic()

try:
    while True:
        estimate_alt = bmp280.altitude
        cali_alt = estimate_alt - init_alt

        if n < window:
            buf.append(cali_alt)
            sma = sum(buf) / len(buf)
        
        else:
            prev_cali = buf[0]
            buf.append(cali_alt)
            sma += (cali_alt - prev_cali) / window

        t = int((time.monotonic() - t0) * 1000)
 
        print(f'raw={cali_alt:8.3f} m | SMA({window})={sma}')
        f.write(f'{t}, {cali_alt:.2f}, {sma:.2f}\n')
        f.flush()

        n += 1
        time.sleep(dt)

except KeyboardInterrupt:
    print('\nterminated')

finally:
    f.close()
